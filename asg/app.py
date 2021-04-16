from flask import Flask #this is a webserver
from flask_graphql import GraphQLView #this is graphql middleware for flask which enables /graphql
import graphene #graphql's processor
from flask import render_template

from getTables import tableSchema #importing schema from python gettables file

app = Flask(__name__) #intialising webserver

# start static query
class QuerySample(graphene.ObjectType):
    message= graphene.String() #message is a property
    name = graphene.String()

    def resolve_message(self, info): #this is a function that gets called when message property is requested
        return 'My first project'
    def resolve_name(self,info):
        return 'hello'

#gschema=graphene.Schema(query=QuerySample) #create graphene schema(graphql schema) from class QuerySample

# end static query

# Flask Rest & Graphql Routes
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=tableSchema,
    graphiql=True,
))

@app.route('/')
def root():
    return render_template("index.html")

#@app.route('/app.js')
#def script():
 #   return render_template("app.js")


if __name__ == '__main__':
    app.run()