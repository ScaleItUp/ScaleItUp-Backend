from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from enum import Enum

app = Flask(__name__)

MONGO_URI = f'mongodb+srv://mini-project:CMZTBb6mt6EF1H6s@miniprojects.kb2cknx.mongodb.net/?retryWrites=true&w=majority'
DB_NAME = 'ScaleKit'
WEIGHTS_COLLECTION = 'Weights'

class StatusCode(Enum):
    SUCCESS = 200
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

# creates a return object for get call of weights
def createWeightObject(statusCode, weights, message):
    return {
        'code': statusCode,
        'data': {
            'weights': weights,
            'message': message
        },
        'message': 'Success'
    }

#test route
@app.route('/')
def hello_world():
    return 'Hello, World!'


# route for getting weights
@app.route('/api/get-weights', methods=['GET'])
# TODO:
# @jwt_required()
def getWeights():
    result = fetchWeightsFromDB()

    if result['isError']:
        returnObject = createErrorObject(
            statusCode=result['statusCode'], message=result['message'])
        return jsonify(returnObject), result['statusCode']
    else:
        returnObject = createWeightObject(
            statusCode=result['statusCode'], weights=result['weights'], message=result['message'])
        return jsonify(returnObject), result['statusCode']
    

# fetches data from the DB
# returns the result object or error object
def fetchWeightsFromDB():
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
            # use this empty array for the return object to be sent
            weights = []
            for weightType in weightsFromDB:
                # if any of these keys are not present, close client and throw exception
                if not weightsCollection.find({'type': {'$exists': True}}) or not weightsCollection.find({'unit_weight': {'$exists': True}}) or not weightsCollection.find({'total_weight': {'$exists': True}}):
                    client.close()
                # add these objects in an array for the response
                else:
                    object = {
                        'type': weightType['type'],
                        'unit_weight': weightType['unit_weight'],
                        'total_weight': weightType['total_weight']
                    }
                    weights.append(object)
        # if both hardwares are not present, throw error
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
            'weights': weights,
            'message': 'Weights Data fetched successfully!'
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