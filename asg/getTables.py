#import pp
from flask import Flask
import os
import sys
import graphene
from graphql import GraphQLError
import logging
import mysql.connector as mysql

import qbe

basedir = os.path.abspath(os.path.dirname(__file__))

class Tables(graphene.ObjectType):
    tblName = graphene.String()
    
class TableStructure (graphene.ObjectType):
   colNames = graphene.List(graphene.String)
    
class Building(graphene.ObjectType):
    bcode = graphene.String()
    bname = graphene.String()

class QueryResult(graphene.ObjectType):
    onerow = graphene.List(graphene.String)

class QBEResult(graphene.ObjectType):
    sql = graphene.String()
    columnHeader = graphene.List(graphene.String)
    queryData = graphene.List(QueryResult)
    

class Queries(graphene.ObjectType):
    tablenames = graphene.List(Tables,userid=graphene.String(),pw=graphene.String(),dbname=graphene.String())
    buildings = graphene.List(Building,val=graphene.String() )
    tablestructure = graphene.List(TableStructure,userid=graphene.String(),pw=graphene.String(),dbname=graphene.String(),tblnamelist= graphene.List(graphene.String),tblCount=graphene.List(graphene.Int))
    qbe = graphene.Field(QBEResult,userid=graphene.String(),pw=graphene.String(),dbname=graphene.String(),columnNames = graphene.List(graphene.String), qbeCmds = graphene.List(graphene.String), conditionBox = graphene.String())

    def resolve_qbe(self, info, userid, pw,dbname,columnNames, qbeCmds, conditionBox):
        print ("Inside resolve maniTables")
        sqlString, header, errMsg = qbe.translate(columnNames,qbeCmds,conditionBox)
        if len(errMsg) > 1:
            raise GraphQLError("ERROR ! " + errMsg)
        db = mysql.connect(
        host="localhost",
        user=userid,
        passwd=pw,
        auth_plugin='mysql_native_password',
        database=dbname
        )
        print (userid, pw, dbname)
        print (sqlString)
        cursor = db.cursor()
        cursor.execute(sqlString)
        data = cursor.fetchall()
        print ('data = ',data)
        #print(pp.pp(cursor, data))
        qData = []
        for row in data:
            row = list(row)   # Convert tuple to a list
            qData.append(QueryResult(onerow=row))
        rtnVal = QBEResult(sql=sqlString,columnHeader=header,queryData=qData)
        return rtnVal


    def resolve_tablenames(self, info, userid, pw,dbname):
        db = mysql.connect(
        host="localhost",
        user=userid,
        passwd=pw,
        auth_plugin='mysql_native_password',
        database=dbname
        )
        query = "SHOW TABLES "
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        tables = []
        for record in records:
            tables.append(Tables(tblName=record[0]))
        return tables
     
   
    def resolve_tablestructure (self, info, userid, pw,dbname,tblnamelist, tblCount):
        db = mysql.connect(
        host="localhost",
        user=userid,
        passwd=pw,
        auth_plugin='mysql_native_password',
        database=dbname
        )
        ColumnNames = []
        #tblnamelist = ["BUILDING","ROOM"]
        logging.info(tblnamelist)
        for i in range(len(tblnamelist)):
            tblrecord = tblnamelist[i]
            for j in range (tblCount[i]):
                tempTable =[]
                tempTable.append(tblrecord)
                query = 'SELECT Column_name, data_type from INFORMATION_SCHEMA.COLUMNS where table_name = "' + tblrecord + '";'
                cursor = db.cursor()
                cursor.execute(query)
                records = cursor.fetchall()
                for record in records:
                    v = record[0].lower() + "("+ record[1].lower() + ")"
                    tempTable.append(v)
                ColumnNames.append(TableStructure(colNames = tempTable ))
        return ColumnNames
   
   ####### SCHEMA ##########

tableSchema = graphene.Schema(query=Queries)
   
        
