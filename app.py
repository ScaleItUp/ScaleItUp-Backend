#imports
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from enum import Enum

#app
app = Flask(__name__)

#config
MONGO_URI = f'mongodb+srv://mini-project:CMZTBb6mt6EF1H6s@miniprojects.kb2cknx.mongodb.net/?retryWrites=true&w=majority'
DB_NAME = 'ScaleKit'
WEIGHTS_COLLECTION = 'Weights'

#enums
class StatusCode(Enum):
    SUCCESS = 200
    CREATION_SUCCESS = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    DATABASE_ERROR = 700
    SERVER_ERROR = 500



# this function creates an error object
# errorType -> to check with errorType
# message -> message returned from exception or a custom message
def createErrorObject(statusCode, message):
    if statusCode is StatusCode.BAD_REQUEST.value:
        return {
            'code': 400,
            'data': {
                'message': message
            },
            'message': 'Failure'
        }
    elif statusCode is StatusCode.NOT_FOUND.value:
        return {
            'code': 404,
            'data': {
                'message': message
            },
            'message': 'Failure'
        }
    elif statusCode is StatusCode.SERVER_ERROR.value:
        return {
            'code': 500,
            'data': {
                'message': message
            },
            'message': 'Failure'
        }
    elif statusCode is StatusCode.DATABASE_ERROR.value:
        return {
            'code': 700,
            'data': {
                'message': message
            },
            'message': 'Failure'
        }

# creates a return object for get call of weight
def createWeightObject(statusCode, weight, message):
    return {
        'code': statusCode,
        'data': {
            'weight': weight,
            'message': message
        },
        'message': 'Success'
    }

# creates a success object with a message and status code
def createSuccessObject(statusCode, message):
    return {
        'code': statusCode,
        'data': {
            'message': message
        },
        'message': 'Success'
    }

#test route
@app.route('/')
def hello_world():
    return 'Hello, World!'


# route for getting weight
@app.route('/api/get-weight', methods=['GET'])
def getWeight():
    result = fetchWeightFromDB()

    if result['isError']:
        returnObject = createErrorObject(
            statusCode=result['statusCode'], message=result['message'])
        return jsonify(returnObject), result['statusCode']
    else:
        returnObject = createWeightObject(
            statusCode=result['statusCode'], weight=result['weight'], message=result['message'])
        return jsonify(returnObject), result['statusCode']
    

# fetches data from the DB
# returns the result object or error object
def fetchWeightFromDB():
    try:
        # Connect to database
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # getting the collection
        weightsCollection = db[WEIGHTS_COLLECTION]

        # Retrieve data from the database and convert to a list of dictionaries
        weightsFromDB = list(weightsCollection.find())

        # check if some data is present
        if len(weightsFromDB) > 0:
            # get the latest weight from db
            weight = weightsFromDB.pop()
            # if any of these keys are not present, close client and throw exception
            if not weightsCollection.find({'weight': {'$exists': True}}):
                client.close()
            # create the object for the response
            else:
                object = weight['weight']
        # if keys are not present, throw error
        else:
            client.close()
            resultObject = {
                'isError': True,
                'statusCode': 700,
                'message': 'Database error: Database doesn\'t have enough data.'
            }
            return resultObject

        client.close()
        # result object for the final response
        resultObject = {
            'isError': False,
            'statusCode': 200,
            'weight': object,
            'message': 'Weight Data fetched successfully!'
        }
        return resultObject

    except PyMongoError as e:
        # Handle database-related errors
        client.close()
        resultObject = {
            'isError': True,
            'statusCode': 700,
            'message': 'Database error: ' + str(e)
        }
        return resultObject
    except Exception as e:
        # Handle other exceptions
        client.close()
        resultObject = {
            'isError': True,
            'statusCode': 500,
            'message': 'Server error: ' + str(e)
        }
        return resultObject

# route for adding a new weight object
@app.route('/api/send-weight', methods=['POST'])
def create_project():

    # storing request project
    weight = request.json['weight']

    result = addWeight(weight)

    if result['isError']:
        returnObject = createErrorObject(
            statusCode=result['statusCode'], message=result['message'])
        return jsonify(returnObject), result['statusCode']
    else:
        returnObject = createSuccessObject(
            statusCode=result['statusCode'], message=result['message'])
        return jsonify(returnObject), result['statusCode']


def addWeight(weight):
    try:
        # Connect to database
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # getting the project collection
        weightsCollection = db[WEIGHTS_COLLECTION]

        # check if the collection is empty or not
        if len(list(weightsCollection.find())) == 0:
            resultObject = {
                'isError': True,
                'statusCode': 404,
                'message': 'Data not found!'
            }
            return resultObject

        # create a new weight object
        newWeight = {
            'weight': weight
        }

        # insert weight in the Weights collection
        weightsCollection.insert_one(newWeight)

        client.close()
        # return the success object
        resultObject = {
            'isError': False,
            'statusCode': 201,
            'message': 'Weight added successfully!',
        }
        return resultObject

    except PyMongoError as e:
        # Handle database-related errors
        client.close()
        resultObject = {
            'isError': True,
            'statusCode': 700,
            'message': 'Database error: ' + str(e)
        }
        return resultObject

    except Exception as e:
        # Handle other exceptions
        client.close()
        resultObject = {
            'isError': True,
            'statusCode': 500,
            'message': 'Server error: ' + str(e)
        }
        return resultObject


# TODO: Remove for deployment
# if __name__ == '__main__':
#     app.run(debug=True)