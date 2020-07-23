import flask, json
from flask import request, jsonify, after_this_request
from run_query import run_query, get_covid_count
from update import main as update

app = flask.Flask(__name__)

@app.route("/", methods=['GET'])
def answer_basic():
    return jsonify("hi! Up and running!")

@app.route("/coords", methods=['GET'])
def answer():
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    lat = str(request.args['lat'])
    lon = str(request.args['lon'])

    try:
        out = run_query([lat, lon])

    except ValueError as e:
        return {"error_message":"Pelo visto, você está fora do Brasil continental. Não quer tentar digitar um endereço?"}

    return jsonify(out)
 
@app.route("/update", methods=['GET'])
def handle_update():
        
    update()

    return jsonify("Aye master, I will update.") 

@app.route("/count", methods=['GET'])
def handle_count():
    '''
    Returns the current number of covid deaths
    in the country and the date it was updated
    '''
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    with open("../output/case_count.json") as file:

        data = json.load(file)

        output = {
            "deaths": data['deaths'],
            "date": data['time'],
            "vanishing_cities": data['vanishing_cities']
            }

    return jsonify(output)

if __name__ == "__main__":
    app.run()
