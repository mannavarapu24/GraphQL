import re
#import pp
import sqlite3
import ast

def translate (columnNamesOrig,qbeCmd,conditionBox):
#    print (columnNamesOrig, len(columnNamesOrig))
#   Since GraplQL does not support list of list, the inner list is passed as a string enclosed in doule quotes and each value in single quotes
#   ast.literal_eval coverts the list as a string to a proper list example below
#   inner list as a string columnNamesOrig
#   ["['BUILDING', 'bcode(char)', 'bname(char)']", "['ROOM', 'bcode(char)', 'rnumber(char)', 'cap(int)', 'layout(char)', 'type(char)', 'dept(char)']"]
#   inner list  converted to a proper list
#   [['BUILDING', 'bcode(char)', 'bname(char)'], ['ROOM', 'bcode(char)', 'rnumber(char)', 'cap(int)', 'layout(char)', 'type(char)', 'dept(char)']]
    errMsg = ""
    for i in range(len(columnNamesOrig)):
        columnNamesOrig[i] = ast.literal_eval(columnNamesOrig[i])
    for i in range(len(qbeCmd)):
        qbeCmd[i] = ast.literal_eval(qbeCmd[i])
    print(columnNamesOrig)

    # Start with two lists. One for Table name and Columns and second one for the QBE commands.
#    columnNamesOrig = [["BUILDING", "bcode(char)", "bname(char)"],["ROOM","bcode(char)","rnumber(char)","cap(int)","layout(char)","type(char)","dept(char)"]]
#    qbeCmd = [["", "_X G. P.", ""],["","_X","COUNT.","MAX.","","",""]]
#    conditionBox = ""
    columnNames = []  # Clean column name without datatype
    columnNamesWithTables = []  # Column names with tables to use in the WHERE clause
    # columnNames   [[BLDG,bcode,bname],[ROOM,bcode,rnum,instr], ["ROOM", "bcode(char)", "rnum(char)", "instr(char)"]]
    # qbeCmd        [["p.", "_x1 "bob".DO(2)", "_X4 .DO(0)G.  >5"], ["", "SUM.", "P. .AO(1)", "P._X5 _X1 AVG."]]
    # conditionBox   "_X1>5_X5 LIKE "...abc..." _X6<7"

    columnHeader = []
    NumTables = len(columnNamesOrig)

    for i in range(NumTables):
        print(i, columnNamesOrig[i][0])
    # Remove data type from ColumnNames
    for i in range(NumTables):
        ColsInOneTbl = []
        for j in range(len(columnNamesOrig[i])):
            if j == 0:
                ColsInOneTbl.append(columnNamesOrig[i][0])
                continue
            oneColName = columnNamesOrig[i][j]
            pos = oneColName.index("(")
            oneColName = oneColName[:pos]
            ColsInOneTbl.append(oneColName)
        columnNames.append(ColsInOneTbl)
    print((columnNamesOrig))
    print(columnNames)
    print(qbeCmd)
    # Remove excess spaces
    for i in range(len(qbeCmd)):
        for j in range(len(qbeCmd[i])):
            oneColName = qbeCmd[i][j].lstrip().rstrip()
            oneColName = re.sub("\s+", " ", oneColName)  # Remove excess blank spaces
            qbeCmd[i][j] = oneColName
    print(qbeCmd)
    # Translate Table Names to Table Names with Occurrence Number
    tbl = []
    tblNames = []
    tblAlias = []
    columnList = []
    for i in range(NumTables):
        oneName = columnNames[i][0]
        if not (oneName in tbl):
            tbl.append(oneName)
            idx = 0
        else:
            idx = 1
        oneAlias = oneName + "_" + str(idx)
        tblNames.append(oneName)
        tblAlias.append(oneAlias)
        # replace Table name in ColumnNames with Alias
        columnNames[i][0] = oneAlias
    print(tblNames)
    print(tblAlias)
    print("Columns having the command P.")
    for i in range(len(qbeCmd)):
        onetbl = columnNames[i]
        onecmd = qbeCmd[i]
        oneColumnNamesWithTable = []
        for j in range(len(onecmd)):
            oneColumnNamesWithTable.append(onetbl[0] + "." + columnNames[i][j])
            if onecmd[j].upper().find("P.") > -1:
                print(onetbl[0], onetbl[j])
                if j == 0:
                    for k in range(1, len(onetbl)):
                        columnList.append(onetbl[0] + "." + onetbl[k])
                        columnHeader.append(onetbl[0] + "." + columnNamesOrig[i][k])
                else:
                    columnList.append(onetbl[0] + "." + onetbl[j])
                    columnHeader.append(onetbl[0] + "." + columnNames[i][j])
        columnNamesWithTables.append(oneColumnNamesWithTable)
    # Look for AVG., MAX. MIN. SUM.
    for i in range(len(qbeCmd)):
        onetbl = oneColumnNamesWithTable[i]
        onecmd = qbeCmd[i]
        for j in range(1,len(onecmd)):        # Skip the Table Name value location 0
            aggKeyword = ""
            if onecmd[j].upper().find("AVG.") > -1 or onecmd[j].upper().find("MAX.") > -1     \
                or onecmd[j].upper().find("MIN.") > -1 or onecmd[j].upper().find("SUM.") > -1 \
                or onecmd[j].upper().find("COUNT.") > -1:
                if onecmd[j].upper().find("AVG.") > -1 : aggKeyword = "AVG"
                if onecmd[j].upper().find("MIN.") > -1 : aggKeyword = "MIN"
                if onecmd[j].upper().find("MAX.") > -1 : aggKeyword = "MAX"
                if onecmd[j].upper().find("SUM.") > -1 : aggKeyword = "SUM"
                if onecmd[j].upper().find("COUNT.") > -1 : aggKeyword = "COUNT"
                if columnNamesWithTables[i][j] in columnList:
                    pos = columnList.index(columnNamesWithTables[i][j])
                    columnList[pos] = aggKeyword + "(" + columnList[pos] + ")"
                    columnHeader[pos] = aggKeyword + "(" + columnHeader[pos] + ")"
                else:
                    columnList.append(aggKeyword + "(" + columnNamesWithTables[i][j] + ")")
                    columnHeader.append(aggKeyword + "(" + columnNamesWithTables[i][j] + ")")
    print("List of Columns are ", columnList)
    print("columnHeader", columnHeader)
    print("All cols with Table name", columnNamesWithTables)
    # Build out colStr
    colStr = ""
    comma = ""
    for i in  range(len(columnList)):
        colStr += comma + " " + columnList[i]
        comma = ","
    ##############################################
    # First remove all AVG. so it does not interfere with G.
    for i in range(len(qbeCmd)):
        for j in range(len(qbeCmd[i])):
            qbeCmd[i][j] = qbeCmd[i][j].replace("AVG.", "").lstrip().rstrip()  # Replace p. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("avg.", "").lstrip().rstrip()  # Replace p. with empty string

    groupBy = ""
    comma = ""
    print("Columns having the command G.")
    for i in range(0, len(qbeCmd)):
        onecmd = qbeCmd[i]
        for j in range(1, len(onecmd)):  # G. is not applicable to the the position 0 (at the table level)
            if onecmd[j].find("G.") > -1 or onecmd[j].find("g.") > -1:
                print(columnNamesWithTables[i][j])
                if len(groupBy) == 0:
                    groupBy = " GROUP BY"
                groupBy += comma + " " + columnNamesWithTables[i][j]
                comma = ","
    print("groupBy ", groupBy)
    ####################################
    listOfColWithAODO = []
    sortCmds = []
    sortVariables = []
    # ------------------------------------  Search for .AO or .DO
    for i in range(len(qbeCmd)):
        for j in range(len(qbeCmd[i])):
            oneSortCond = []
            oneColName = qbeCmd[i][j].lstrip().rstrip().upper()
            if oneColName.upper().find(".AO") > -1 or oneColName.upper().find(".DO") > -1:
                pos = oneColName.upper().find(".AO")
                if pos > -1:
                    print("Found .AO in ", oneColName, "at position ", pos)
                    sortOrder = "ASC"
                else:
                    pos = oneColName.upper().find(".DO")
                    if pos > -1:
                        print("Found .DO in ", oneColName, "at position ", pos)
                        sortOrder = "DESC"
                if (oneColName.find("(", pos)) > -1:  # Sort rank is specified
                    rankStartPos = oneColName.find("(", pos)
                    rankEndPos = oneColName.find(")", pos)
                    rank = oneColName[rankStartPos + 1:rankEndPos]
                    print("Rank = ", rank)
                    oneVariable = oneColName[pos:rankEndPos + 1]
                else:  # .AO or .DO without parentheses
                    oneVariable = oneColName[pos:pos + 4]
                    rank = 0
                oneSortCond.append(columnNamesWithTables[i][j])
                oneSortCond.append(sortOrder)
                oneSortCond.append(rank)
                oneSortCond.append(oneVariable)
                listOfColWithAODO.append(oneSortCond)
                sortVariables.append(oneVariable)
    print("Cols with AO and DO ", listOfColWithAODO)
    # From Clause
    fromClause = " FROM"
    comma = ""
    for i in range(len(tblNames)):
        fromClause += comma + " " + tblNames[i] + " " + tblAlias[i]
        comma = ","
    print("fromClause = ", fromClause)

    # Now the WHERE Clause
    # Extract variables and make association
    # First remove all the P. and p. as we have addressed it
    for i in range(len(qbeCmd)):
        for j in range(len(qbeCmd[i])):
            qbeCmd[i][j] = qbeCmd[i][j].replace("P.", "").lstrip().rstrip()  # Replace P. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("p.", "").lstrip().rstrip()  # Replace p. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("G.", "").lstrip().rstrip()  # Replace G. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("g.", "").lstrip().rstrip()  # Replace g. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("SUM.", "").lstrip().rstrip()  # Replace SUM. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("sum.", "").lstrip().rstrip()  # Replace sum. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("MIN.", "").lstrip().rstrip()  # Replace MIN. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("min.", "").lstrip().rstrip()  # Replace min. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("MAX.", "").lstrip().rstrip()  # Replace MAX. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("max.", "").lstrip().rstrip()  # Replace max. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("COUNT.", "").lstrip().rstrip()  # Replace COUNT. with empty string
            qbeCmd[i][j] = qbeCmd[i][j].replace("count.", "").lstrip().rstrip()  # Replace count. with empty string
    print("QBE command after removal of P. G. MAX. MIN. COUNT. AVG. SUM. ", qbeCmd)
    compareList = []
    variables = []  # all UPPER case
    variablesOrig = []  # Mixed case
    variableCount = {}  # dict to store the number of times the variable is defined
    # Now look for all the variables words beginning with _ (Note: there has to be no space between commands such as >100 <200 etc)

    delimiters = "._()><= "
    for i in range(len(qbeCmd)):
        for j in range(len(qbeCmd[i])):
            oneColName = qbeCmd[i][j]
            tmp = []
            splitstr = ""         # split based on _ Retain _ in the split string list
 #          print("oneColName = ",oneColName)
            for z in range(len(oneColName)):
                if z == len(oneColName) - 1:   # at end last char of the string
                    splitstr += oneColName[z:z + 1]
                    tmp.append(splitstr)
                else:
                    if oneColName[z:z+1] != "_" :
                        splitstr += oneColName[z:z+1]
                    else:
                        tmp.append(splitstr)
                        splitstr = "_"
            lst = []
            for z in tmp:
                tempz = z.split(" ")  # Split each value on space
                for zz in tempz:
                    if len(zz) > 0:
                        lst.append(zz)
#           print ("lst = ",lst)
            for k in range(len(lst)):
#               print ("one lst is ",lst[k])
                if lst[k][0:1] == "_":
                    cmpPair = []
                    oneVariable = "_"
                    for z in range(1,len(lst[k])):
                        nextchar = lst[k][z:z+1]     #get one  char at a time
                        if nextchar in delimiters:
                            break
                        oneVariable += nextchar
                    cmpPair.append(oneVariable.upper())
                    cmpPair.append(columnNamesWithTables[i][j])
                    if oneVariable.upper() in variables:
                        variableCount[oneVariable.upper()] = variableCount[oneVariable.upper()] + 1
                        compareList[variables.index(oneVariable.upper())].append(columnNamesWithTables[i][j])
                    else:
                        variableCount[oneVariable.upper()] = 1
                        variables.append(oneVariable.upper())
                        compareList.append(cmpPair)
                    if not (oneVariable in variablesOrig):
                        variablesOrig.append(oneVariable)
    print("CompareList", compareList)
    print("Variables (UPPER Case)", variables)
    print("variables Original (Mixed Case)", variablesOrig)
    print("Count of variables", variableCount)
    #
    # Now that we have all the variables remove them from the qbe string
    for k in range(len(variablesOrig)):
        print("removing variable " + variablesOrig[k])
        for i in range(len(qbeCmd)):
            for j in range(len(qbeCmd[i])):
                oneColName = qbeCmd[i][j]
                qbeCmd[i][j] = oneColName.replace(variablesOrig[k], "").lstrip().rstrip()  # Replace _Variable with empty string
    print("QBE command after removal of ALL Variables ", qbeCmd)
    # Now remove Sort variables from the qbe string
    for k in range(len(sortVariables)):
        print("removing variable " + sortVariables[k])
        for i in range(len(qbeCmd)):
            for j in range(len(qbeCmd[i])):
                oneColName = qbeCmd[i][j]
                qbeCmd[i][j] = oneColName.replace(sortVariables[k], "").lstrip().rstrip()  # Replace Sort Variable with empty string
    print("QBE command after removal of ALL SORT Variables ", qbeCmd)
    whereStr = " WHERE 1 = 1 "
    for i in range(len(compareList)):  # print(compareList[i],len(compareList[i]))
        # Compare value 1 and 2 the two compare Columns - pos 0 is the variablename ["_X1", "BLDG_0.bcode", "ROOM_0.bcode", "ROOM_0.instr"]
        # loop to (n - 2) conditions
        if len(compareList[i]) > 2:  # We have atleast 3 items in the compare list - Variable plus two columns
            for j in range(2, len(compareList[i])):
                whereStr += " AND " + compareList[i][1] + " = " + compareList[i][j]
        else:
            print("Variable Ignored ", compareList[i][0])
    print("Where Clause ", whereStr)
# Parse basic conditions in the Column Commands
    for i in range(len(qbeCmd)):
        for j in range(1,len(qbeCmd[i])):       # ignore Table position 0
            cond = qbeCmd[i][j]                 #remaining string after all Variables and . Commands are removed
            if cond in ["P","G"]:
                errMsg = "QBE command parsing error, Missing period (.), Expecting cmd " + cond + " to end with a ."
                return "", "", errMsg
            if cond in ["OA","OD"]:
                errMsg = "QBE command parsing error, Missing period (.), Expecting cmd " + cond + " to begin with a ."
                return "", "", errMsg
            if len(cond) > 1:
                if cond[0:1] in "><=":
                    whereStr += " AND " + columnNamesWithTables[i][j] + " " + cond
                else:
                    whereStr += " AND " + columnNamesWithTables[i][j] + "=" + cond     # if no condition specified default to =
    # Parse the Condition Box
    delimiters = "._()><= "
    conditionBox = re.sub("\s+", " ", conditionBox)  # Remove excess blank spaces
    conditionBox = conditionBox.lstrip().rstrip()
    conditionList = []  # List of conditions
    lst = conditionBox.split("_")
#   print("lst = ", lst)
    # lst = conditionBox.split()  # Split on underscore
    for i in range(len(lst)):
        oneCond = lst[i].lstrip().rstrip()
        oneVar = ""
        if oneCond == "":
            continue
        cnt = 0
        if oneCond.find("'") > 0 :       # find a '
            cnt = oneCond.count("'")
        if oneCond.find('"') > 0:        #"find a '
            cnt = oneCond.count("'")
        if cnt != 0 :
           if cnt != 2  :        # Quotes are not matching
              errMsg = "QBE command parsing error, Missing quote in cmd " + oneCond
              return "", "", errMsg
        print("working wth _" + oneCond, "length", len(oneCond))
        for j in range(len(oneCond)):
            ch = oneCond[j:j + 1]
            if not (ch in delimiters):
                oneVar += ch
            else:  # delimiter encountered
                oneVar = "_" + oneVar  # Add preceding _
                print("variable ", oneVar)
                if oneVar in variables:
                    idx = variables.index(oneVar)
                    column = compareList[idx][1]
#                   print(column)
                    condition = oneCond[j:]
                    print("Condition =", condition)
                    conditionList.append([column, condition])
                else:
                    print("Unable to resolve Variable ", oneVar, "In Condition Box")
                break
    print("ConditionList", conditionList)
    for i in range(len(conditionList)):
        whereStr += " AND " + conditionList[i][0] + conditionList[i][1]  # Compare value 1 and 2
    print("Where Clause ", whereStr)
    print("-" * 50)  # Print 50 dashes
    ##Add SORT clause
    if len(listOfColWithAODO) > 0:
        orderBy = " ORDER BY "
    else:
        orderBy = ""
    comma = ""
    maxRank = 0
    for i in range(len(listOfColWithAODO)):
        if int(listOfColWithAODO[i][2]) > maxRank:
            maxRank = int(listOfColWithAODO[i][2])
    for i in range(maxRank + 1):
        for j in range(len(listOfColWithAODO)):
            if i == int(listOfColWithAODO[j][2]):
                orderBy += comma + " " + listOfColWithAODO[j][0] + " " + listOfColWithAODO[j][1]
                comma = ","
    print("ORDER BY", orderBy)
    query = "SELECT " + colStr + fromClause + whereStr + groupBy + orderBy + ";"
    print(query)
    print(columnHeader)

    return query, columnHeader, errMsg

if __name__ == "__main__":
#    columnNamesOrig = [["BUILDING", "bcode(char)", "bname(char)"],["ROOM","bcode(char)","rnumber(char)","cap(int)","layout(char)","type(char)","dept(char)"]]
    columnNamesOrig = ["['BUILDING', 'bcode(char)', 'bname(char)']", "['ROOM', 'bcode(char)', 'rnumber(char)', 'cap(int)', 'layout(char)', 'type(char)', 'dept(char)']"]
    qbeCmd = ["['', '_X_K> G. P.', '']","['','_X','P.','P.<200_Q','','','']"]
#    qbeCmd = [["", "_X G. P.", ""],["","_X","P.","MAX.","","",""]]
    conditionBox = "_Q>100"
    query, columnHeader, errMsg = translate(columnNamesOrig, qbeCmd, conditionBox)
    con = sqlite3.connect("qbe.sqlite")
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    #print(pp.pp(cur, data))