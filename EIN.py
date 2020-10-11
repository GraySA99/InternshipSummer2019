# Electronics Inventory Notetaker
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import ttkthemes as ThemedTk
import tempfile
import win32api
from tkinter.ttk import *
import requests
from tkcalendar import *
import babel
import babel.numbers
import math
import hashlib
import datetime as dt
import mysql.connector
import base64
import os
import win32print
import sqlite3

# ------------------------------SQL----------------------------------------
#This method creates the assets table
def createTable():
    SQLC = '''
        CREATE TABLE IF NOT EXISTS assets (
        asset_name VARCHAR(20) PRIMARY KEY,
        asset_tag VARCHAR(20),
        serial_num VARCHAR(20),
        make VARCHAR(20),
        model VARCHAR(20),
        category VARCHAR(20),
        status VARCHAR(20),
        location VARCHAR(20),
        date_bought VARCHAR(20),
        notes VARCHAR(180000),
        created_by VARCHAR(20),
        created_at VARCHAR(20),
        last_editor VARCHAR(20),
        last_editat VARCHAR(20)
        );
    '''
    crsr.execute(SQLC)
    connection.commit()

#This method returns true if an asset with asset name aName is in the table desiredInfo
# returns false otherwise
def isItemAvailable(aName, desiredInfo):
    SQLC = '''
        SELECT ''' + desiredInfo + ''' FROM assets
        WHERE asset_name = \'''' + aName + '''\';
    '''
    crsr.execute(SQLC)

    return crsr.fetchall() == []

#Inserts asset with information found within iList into table tableName
def insertIntoTable(iList, tableName):

    global currentUser
    SQLC = '''
        SELECT * FROM ''' + tableName + '''
        WHERE asset_name = \"''' + iList[0].strip() + '''\";
    '''
    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    if not tmp:
        SQLC = '''
            INSERT INTO ''' + tableName + ''' VALUES(\"''' + iList[0].strip() + '\", \"' + iList[1].strip() + '\", \"' \
            + iList[2].strip() + '\", \"' + iList[3].strip() + '\", \"' + iList[4].strip() + '\", \"' \
            + iList[5].strip() + '\", \"' + iList[6].strip() + '\", \"' + iList[7].strip() + '\", \"' \
            + iList[8].strip() + '\", \"' + iList[9].strip() + '\", \"'+ currentUser + '-' + os.environ['COMPUTERNAME'] + '\", \"' \
            + getTimeDate() + '\", \"' + currentUser + '-' + os.environ['COMPUTERNAME'] + '\", \"' + getTimeDate() + '''\"); 
            '''
        crsr.execute(SQLC)
        connection.commit()
    else:
        messagebox.showinfo('Problem Occurred', iList[0] + ' Already Exists\nTry using the edit tab')

#This method drops the assets table
def dropTable():

    SQLC = '''
        DROP TABLE assets;
    '''
    crsr.execute(SQLC)
    connection.commit()

#This method prints the assets table
def printTable():

    SQLC = '''
        SELECT * FROM assets;
    '''

    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    for i in tmp:
        print(i)

#This method creates the deprecated table
def createDepTable():

    SQLC = '''
        CREATE TABLE IF NOT EXISTS deprecated (
        asset_name VARCHAR(20) PRIMARY KEY,
        asset_tag VARCHAR(20),
        serial_num VARCHAR(20),
        model VARCHAR(20),
        category VARCHAR(20),
        status VARCHAR(20),
        location VARCHAR(20),
        date_bought VARCHAR(20),
        make VARCHAR(20),
        notes VARCHAR(180000),
        created_by VARCHAR(20),
        created_at VARCHAR(20),
        last_editor VARCHAR(20),
        last_editat VARCHAR(20)
        );
    '''

    crsr.execute(SQLC)
    connection.commit()

#This method drops the deprecated table
def dropDepTable():

    SQLC = '''
        DROP TABLE deprecated;
    '''

    crsr.execute(SQLC)
    connection.commit()

#This method prints the deprecated table
def printDepTable():

    SQLC = '''
            SELECT * FROM deprecated;
        '''

    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    for i in tmp:
        print(i)

#This method creates the logins table
def createLoginTable():
    SQLC = '''
        CREATE TABLE IF NOT EXISTS logins (
        usr_name VARCHAR(20) PRIMARY KEY,
        password VARCHAR(70),
        status VARCHAR(20),
        is_guest BIT
        );
    '''
    crsr.execute(SQLC)
    connection.commit()

    SQLC = '''
    SELECT * FROM logins
    WHERE usr_name = "admin"
    '''
    crsr.execute(SQLC)
    if len(crsr.fetchall()) == 0:

        hasher = hashlib.sha256()
        hasher.update(bytes('admin', encoding='utf-8'))
        SQLC = '''
            INSERT INTO logins VALUES(\"admin\", \"''' + hasher.hexdigest() + '''\", \"offline\", 0);
        '''
        crsr.execute(SQLC)
        connection.commit()

#This method drops the logins table
def dropLoginTable():

    SQLC = '''
        DROP TABLE logins;
    '''

    crsr.execute(SQLC)
    connection.commit()

#This method prints the logins table
def printLoginTable():
    SQLC = '''
            SELECT * FROM logins;
        '''

    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    for i in tmp:
        print(i)

def createStatusTable():

    SQLC = '''
        CREATE TABLE IF NOT EXISTS status (
            name VARCHAR(20) PRIMARY KEY
        );
    '''
    crsr.execute(SQLC)
    connection.commit()

def dropStatusTable():

    SQLC = '''
        DROP TABLE status;
    '''
    crsr.execute(SQLC)
    connection.commit()

def printStatusTable():

    crsr.execute('SELECT * FROM status')

    for x in crsr.fetchall():
        print(x)

def createCatTable():

    SQLC = '''
        CREATE TABLE IF NOT EXISTS category (
            name VARCHAR(20) PRIMARY KEY
        );
    '''
    crsr.execute(SQLC)
    connection.commit()

def dropCatTable():

    SQLC = '''
        DROP TABLE category;
    '''
    crsr.execute(SQLC)
    connection.commit()

def printCatTable():

    crsr.execute('SELECT * FROM category')

    for x in crsr.fetchall():
        print(x)

# ----------------------------Methods------------------------------------
#This method takes the Entry fields for the InsertionTab and formats them into the textbox in the InsertionTab
def pushEnt():

    global insertResults
    global currentUser
    global currentNotesInsert
    global insertNotes

    def searchForInsert(event):

        index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))\

        boxOption = messagebox.askquestion('Remove Asset?', 'Would you like to remove this asset from the list?')

        if boxOption == 'yes':
            text.config(state = 'normal')
            text.delete(str(index) + '.0', str(index + 1) + '.0')
            text.config(state = 'disabled')

    if len(str(assetName.get()).strip()) == 0:
        messagebox.showinfo('Asset Name Needed', 'An Asset Name is Required For An Entry\nPlease Try Again.')
    elif len(str(assetName.get())) > 20 or len(str(assetTag.get())) > 20 or len(str(serialNum.get())) > 20\
        or len(str(model.get())) > 20 or len(str(assetName.get())) > 20 or len(str(cat.get())) > 20\
            or len(str(status.get())) > 20 or len(str(location.get())) > 20:
        messagebox.showinfo('Input Length Error', 'All fields must be under 20 characters long\nPlease try again')
    elif validateInput(assetName.get()) or validateInput(assetTag.get()) or validateInput(serialNum.get())\
        or validateInput(model.get()) or validateInput(cat.get()) or validateInput(status.get()) \
        or validateInput(location.get()) or validateInput(make.get()) or validateInput(currentNotesInsert):
        messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                               '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
    else:
        tmp = ''
        tmp += ('' + assetName.get() + ', ')
        tmp += ('' + assetTag.get() + ', ')
        tmp += ('' + serialNum.get() + ', ')
        tmp += ('' + make.get() + ', ')
        tmp += ('' + model.get() + ', ')
        tmp += ('' + cat.get() + ', ')
        tmp += ('' + status.get() + ', ')
        tmp += ('' + location.get() + ', ')

        if dBought['text'] != 'Choose Date':
            tmp += ('' + dBought['text'] + ',')
        else:
            tmp += ', '

        tmp += ('' + str(len(insertNotes) + 1) + '')
        insertNotes.append(currentNotesInsert)
        currentNotesInsert = ''

        text.config(state='normal')
        text.insert(1.0, str(tmp)[int(str(tmp).find(',')):] + '\n')
        tag = 'insert' + str(tmp)[0:int(str(tmp).find(','))]
        text.tag_config(str(tag), foreground = 'blue')
        text.tag_bind(str(tag), '<Button-1>', lambda e: searchForInsert(e))
        text.insert(1.0, str(tmp)[0:int(str(tmp).find(','))], str(tag))
        text.config(state='disabled')

        assetName.delete(0, END)
        assetTag.delete(0, END)
        serialNum.delete(0, END)
        model.delete(0, END)
        cat.delete(0, END)
        status.delete(0, END)
        location.delete(0, END)
        make.delete(0, END)
        notesBtn.config(text = 'Insert Note')
        dBought.config(text = 'Choose Date')

#This method removes the first line of the textbox in the InsertionTab
def delPrevEnt():
    text.config(state='normal')
    text.delete(1.0, 2.0)
    text.config(state='disabled')

#This method takes all entries within the textbox in the InsertionTab and properly formats
#   and adds them as entries into the asset table
def DBExport():

    if check_internet():
        global insertNotes
        temp = text.get('1.0', END)
        if temp.strip() != '':
            temp = temp.splitlines()
            for i in temp:

                if i.strip() != '':
                    i = i.split(',')
                    i[9] = insertNotes[int(i[9]) - 1]
                    insertIntoTable(i, 'assets')

            messagebox.showinfo('Operation Successful', 'Information Successfully Exported to Database')
            text.config(state = 'normal')
            text.delete('1.0', END)
            text.config(state = 'disabled')
        insertNotes = []

#This method takes in all filter search requirements specified by the user
# and searched for assets within the assets table and displays them with textbox found in the searchTab
def search():

    if check_internet():
        global searchResults
        searchResults = {}

        def notesSearch(event):

            global currentNotesEdit
            index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))

            SQLC = '''
                SELECT notes FROM assets
                WHERE asset_name = \"''' + searchResults[str(index)] + '''\";
            '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()
            tmp = tmp[0][0]

            tmpRoot = Toplevel()
            tmpRoot.title('Notes For ' + searchResults[str(index)])
            tmpRoot.grab_set()
            tmpRoot.geometry('350x350')
            icondata = base64.b64decode(icon)
            tempFile = "icon.ico"
            iconfile = open(tempFile, "wb")
            iconfile.write(icondata)
            iconfile.close()
            tmpRoot.wm_iconbitmap(tempFile)
            os.remove(tempFile)
            center(tmpRoot)

            textContainerNotes = Frame(tmpRoot, borderwidth=1, relief='sunken')
            textNotes = Text(textContainerNotes, font=('Courier', 10), width=30, height=30, wrap='none', borderwidth=0)
            textVsbNotes = Scrollbar(textContainerNotes, orient="vertical", command=textNotes.yview)
            textHsbNotes = Scrollbar(textContainerNotes, orient="horizontal", command=textNotes.xview)
            textNotes.configure(yscrollcommand=textVsbNotes.set, xscrollcommand=textHsbNotes.set, state='disabled')
            textNotes.grid(row=0, column=0, sticky=N + S + W + E)
            textVsbNotes.grid(row=0, column=1, sticky=N + S + W + E)
            textHsbNotes.grid(row=1, column=0, sticky=N + S + W + E)
            for x in range(1):
                Grid.rowconfigure(textContainerNotes, x, weight=1)
            Grid.columnconfigure(textContainerNotes, 0, weight=1)
            Grid.columnconfigure(textContainerNotes, 1, weight=0)
            textNotes.config(state = 'normal')
            textNotes.insert('1.0', tmp)
            textNotes.config(state='disabled')

            #Grid Building
            textContainerNotes.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
            Grid.rowconfigure(tmpRoot, 0, weight = 1)
            Grid.columnconfigure(tmpRoot, 0, weight = 1)


        def searchForEdit(event):

            global currentNotesEdit
            index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))

            SQLC = '''
                        SELECT * FROM assets
                        WHERE asset_name = \"''' + searchResults[str(index)] + '''\";
                    '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()
            tmp = tmp[0]
            changeEditEnts('normal')
            assetNameEditEnt.config(state = 'normal')
            assetNameEditEnt.delete(0, END)
            assetNameEditEnt.insert(0, tmp[0])
            assetTagEditEnt.delete(0, END)
            assetTagEditEnt.insert(0, tmp[1])
            serialNumEditEnt.delete(0, END)
            serialNumEditEnt.insert(0, tmp[2])
            makeEditEnt.delete(0, END)
            makeEditEnt.insert(0, tmp[3])
            modelEditEnt.delete(0, END)
            modelEditEnt.insert(0, tmp[4])
            catEditEnt.delete(0, END)
            catEditEnt.insert(0, tmp[5])
            statusEditCombo.delete(0, END)
            statusEditCombo.insert(0, tmp[6])
            locationEditEnt.delete(0, END)
            locationEditEnt.insert(0, tmp[7])
            dBoughtEditEnt.config(text = tmp[8])
            notesEditBtn.config(text = str(tmp[9])[0:6].strip() + '...')
            currentNotesEdit = tmp[9]
            assetNameEditEnt.config(state='disabled')
            findBtn.config(state='disabled')
            delEntBtn.config(state = 'normal')
            updateBtn.config(state='normal')
            clearBtn.config(state='normal')
            tabControl.select(editTab)

        textSearchOne.config(state = 'normal')
        textSearchOne.delete('1.0', END)
        textSearchOne.config(state = 'disabled')
        textSearchTwo.config(state = 'normal')
        textSearchTwo.delete('1.0', END)
        textSearchTwo.config(state = 'disabled')

        SQLC = '''
            SELECT * FROM assets
            WHERE
        '''

        if validateInput(assetNameSearchEnt.get()) or validateInput(assetTagSearchEnt.get())\
            or validateInput(serialNumSearchEnt.get()) or validateInput(modelSearchEnt.get())\
            or validateInput(catSearchEnt.get()) or validateInput(statusSearchCombo.get())\
            or validateInput(locationSearchEnt.get()) or validateInput(makeSearchEnt.get()):
            messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                   '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
        else:
            if assetNameSearchEnt.get().strip() != '':
                SQLC += '''
                    asset_name = \"''' + assetNameSearchEnt.get().strip() + '''\" AND
                '''
            if assetTagSearchEnt.get().strip() != '':
                SQLC += '''
                    asset_tag = \"''' + assetTagSearchEnt.get().strip() + '''\" AND
                '''
            if serialNumSearchEnt.get().strip() != '':
                SQLC += '''
                    serial_num = \"''' + serialNumSearchEnt.get().strip() + '''\" AND
                '''
            if makeSearchEnt.get().strip() != '':
                SQLC += '''
                    make = \"''' + makeSearchEnt.get().strip() + '''\" AND
                '''
            if modelSearchEnt.get().strip() != '':
                SQLC += '''
                    model = \"''' + modelSearchEnt.get().strip() + '''\" AND
                '''
            if catSearchEnt.get().strip() != '':
                SQLC += '''
                    category = \"''' + catSearchEnt.get().strip() + '''\" AND
                '''
            if statusSearchCombo.get().strip() != '':
                SQLC += '''
                    status = \"''' + statusSearchCombo.get().strip() + '''\" AND
                '''
            if locationSearchEnt.get().strip() != '':
                SQLC += '''
                    location = \"''' + locationSearchEnt.get().strip() + '''\" AND
                '''
            if dBoughtSearchEnt['text'].strip() != 'Choose Date':
                SQLC += '''
                    date_bought = \"''' + dBoughtSearchEnt['text'].strip() + '''\" AND
                '''
            if noteSearchEnt.get().strip() != '':
                SQLC += '''
                    UPPER(notes) LIKE UPPER(\"%''' + noteSearchEnt.get().strip() + '''%\")
                '''

            if SQLC.strip()[-3:] == 'AND':
                SQLC = SQLC.strip()[:-3]
            if SQLC.strip()[-5:] == 'WHERE':
                SQLC = '''
                SELECT * FROM assets;
                '''

            crsr.execute(SQLC)
            textSearchOne.config(state='normal')
            textSearchTwo.config(state='normal')
            textSearchZero.config(state='normal')
            textSearchZero2.config(state='normal')
            tmp = crsr.fetchall()
            tmp.sort()

            for i in tmp:
                for j in range(len(i)):
                    if j == 0 and not isUserGuest(currentUser):
                        tag = 'search' + i[j]
                        searchResults[str(len(searchResults) + 1)] = i[j]
                        textSearchOne.tag_config(str(tag), foreground = 'blue')
                        textSearchOne.tag_bind(tag, '<Button-1>', lambda e:searchForEdit(e))
                        textSearchOne.insert(END, stringGridFormat(i[j]), tag)
                        textSearchOne.insert(END, '|')
                    elif j == 0 and isUserGuest(currentUser):
                        searchResults[str(len(searchResults) + 1)] = i[j]
                        textSearchOne.insert(END, stringGridFormat(i[j]) + '|')
                    elif j == 9:
                        tag = 'searchNotes' + str(j)
                        textSearchTwo.tag_config(str(tag), foreground='blue')
                        textSearchTwo.tag_bind(tag, '<Button-1>', lambda e: notesSearch(e))
                        textSearchTwo.insert(END, stringGridFormat('notes'), tag)
                        textSearchTwo.insert(END, '|')
                    elif j+1 == len(i):
                        textSearchTwo.insert(END, stringGridFormat(i[j]))
                    else:
                        textSearchTwo.insert(END, stringGridFormat(i[j]) + '|')
                textSearchTwo.insert(END, '\n')
                textSearchOne.insert(END, '\n')

            textSearchZero2.insert('1.0', '--------------------\n')
            textSearchZero.insert('1.0', '\n--------------------|\n')
            for i in range(0,12):
                textSearchZero2.insert('1.0', '--------------------' + '|')
            textSearchZero2.insert('1.0', '\n')
            textSearchZero2.insert('1.0', stringGridFormat('Last Edited'))
            textSearchZero2.insert('1.0', stringGridFormat('Last Editor') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Created At') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Created By') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Notes') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Date Bought') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Location') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Status') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Category') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Model') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Make') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Serial Number') + '|')
            textSearchZero2.insert('1.0', stringGridFormat('Asset Tag') + '|')
            textSearchZero.insert('1.0', stringGridFormat('Asset Name') + '|')
            textSearchOne.config(state = 'disabled')
            textSearchTwo.config(state = 'disabled')
            textSearchZero.config(state = 'disabled')
            textSearchZero2.config(state = 'disabled')
    else:

        def recon(event):

            reconnect()
            if check_internet():
                search()
            else:
                clearSearch()
                tag = 'reconnect'
                textSearchTwo.tag_config(str(tag), foreground='red')
                textSearchTwo.tag_bind(str(tag), '<Button-1>', recon)
                textSearchTwo.config(state='normal')
                textSearchTwo.insert(END, 'Reconnect To Server', str(tag))
                textSearchTwo.config(state='disabled')

        clearSearch()
        tag = 'reconnect'
        textSearchTwo.tag_config(str(tag), foreground='red')
        textSearchTwo.tag_bind(str(tag), '<Button-1>', recon)
        textSearchTwo.config(state = 'normal')
        textSearchTwo.insert(END, 'Reconnect To Server', str(tag))
        textSearchTwo.config(state = 'disabled')

#This method properly formats word with the correct amount of spaces for displaying search results
def stringGridFormat(word):

    max = 20
    while len(word) < max:
        word = ' ' + word + ' '
    if len(word) > max:
        word = word[0:max]
    return word

#This method finds the asset information for the asset with asset name specified by assetNameEditEnt
def findAsset():

    if check_internet():
        global currentNotesEdit

        if assetNameEditEnt.get().strip() != '':

            SQLC = '''
                SELECT * FROM assets
                WHERE asset_name = \"''' + assetNameEditEnt.get() + '''\";
            '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()
            if tmp:
                tmp = tmp[0]
                changeEditEnts('normal')
                assetNameEditEnt.delete(0, END)
                assetNameEditEnt.insert(0, tmp[0])
                assetTagEditEnt.delete(0, END)
                assetTagEditEnt.insert(0, tmp[1])
                serialNumEditEnt.delete(0, END)
                serialNumEditEnt.insert(0, tmp[2])
                makeEditEnt.delete(0, END)
                makeEditEnt.insert(0, tmp[3])
                modelEditEnt.delete(0, END)
                modelEditEnt.insert(0, tmp[4])
                catEditEnt.delete(0, END)
                catEditEnt.insert(0, tmp[5])
                statusEditCombo.delete(0, END)
                statusEditCombo.insert(0, tmp[6])
                locationEditEnt.delete(0, END)
                locationEditEnt.insert(0, tmp[7])
                dBoughtEditEnt.config(text = tmp[8])
                notesEditBtn.config(text = str(tmp[9])[0:6].strip() + '...')
                currentNotesEdit = tmp[9]
                assetNameEditEnt.config(state = 'disabled')
                findBtn.config(state = 'disabled')
                updateBtn.config(state = 'normal')
                clearBtn.config(state = 'normal')
                delEntBtn.config(state = 'normal')
            else:
                messagebox.showinfo('Problem Occurred', assetNameEditEnt.get() + ' does not exist')

#This method is a shortcut for setting entry fields to a specific state, s
def changeEditEnts(s):

    assetTagEditEnt.config(state=s)
    serialNumEditEnt.config(state=s)
    modelEditEnt.config(state=s)
    catEditEnt.config(state=s)
    statusEditCombo.config(state=s)
    locationEditEnt.config(state=s)
    dBoughtEditEnt.config(state=s)
    makeEditEnt.config(state=s)
    notesEditBtn.config(state=s)

#This method updates a specified asset with asset name assetNameEditEnt
def update():

    if check_internet():
        global currentUser

        if dBoughtEditEnt['text'] == 'Choose Date':
            SQLC = '''
                UPDATE assets
                SET
                    date_bought = \"\"
                WHERE asset_name = \"''' + assetNameEditEnt.get().strip() + '''\";
            '''
            crsr.execute(SQLC)
            connection.commit()
        else:
            SQLC = '''
                UPDATE assets
                SET
                    date_bought = \"''' + dBoughtEditEnt['text'] + '''\"
                WHERE asset_name = \"''' + assetNameEditEnt.get().strip() + '''\";
            '''
            crsr.execute(SQLC)
            connection.commit()


        if validateInput(assetTagEditEnt.get()) or validateInput(serialNumEditEnt.get()) or validateInput(modelEditEnt.get())\
            or validateInput(catEditEnt.get()) or validateInput(statusEditCombo.get()) or validateInput(locationEditEnt.get())\
            or validateInput(makeEditEnt.get()) or validateInput(currentNotesEdit):
            messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                   '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
        else:
            SQLC = '''
                UPDATE assets
                SET
                    asset_tag = \"''' + assetTagEditEnt.get().strip() + '''\",
                    serial_num = \"''' + serialNumEditEnt.get().strip() + '''\",
                    model = \"''' + modelEditEnt.get().strip() + '''\",
                    category = \"''' + catEditEnt.get().strip() + '''\",
                    status = \"''' + statusEditCombo.get().strip() + '''\",
                    location = \"''' + locationEditEnt.get().strip() + '''\",
                    make = \"''' + makeEditEnt.get().strip() + '''\",
                    notes = \"''' + currentNotesEdit.strip() + '''\",
                    last_editor = \"''' + currentUser + '-' + os.environ['COMPUTERNAME'] + '''\",
                    last_editat = \"''' + getTimeDate() + '''\"
                WHERE asset_name = \"''' + assetNameEditEnt.get().strip() + '''\";
            '''

            crsr.execute(SQLC)
            connection.commit()
            messagebox.showinfo('Operation Successful', assetNameEditEnt.get() + ' successfully updated')
            clearSearch()
            assetNameEditEnt.config(state = 'normal')
            assetNameEditEnt.delete(0, END)
            assetTagEditEnt.delete(0, END)
            serialNumEditEnt.delete(0, END)
            modelEditEnt.delete(0, END)
            catEditEnt.delete(0, END)
            statusEditCombo.delete(0, END)
            locationEditEnt.delete(0, END)
            makeEditEnt.delete(0, END)
            dBoughtEditEnt.config(text = 'Choose Date')
            notesEditBtn.config(text = 'Edit Notes')
            changeEditEnts('disabled')
            updateBtn.config(state = 'disabled')
            clearBtn.config(state = 'disabled')
            delEntBtn.config(state = 'disabled')
            findBtn.config(state = 'normal')

#This method is a shortcut to clear the Edit Entry fields on the editTab
def clearEdit():
    assetNameEditEnt.config(state='normal')
    assetNameEditEnt.delete(0, END)
    assetTagEditEnt.delete(0, END)
    serialNumEditEnt.delete(0, END)
    modelEditEnt.delete(0, END)
    catEditEnt.delete(0, END)
    statusEditCombo.delete(0, END)
    locationEditEnt.delete(0, END)
    makeEditEnt.delete(0, END)
    dBoughtEditEnt.config(text = 'Choose Date')
    notesEditBtn.config(text = 'Edit Notes')
    changeEditEnts('disabled')
    updateBtn.config(state = 'disabled')
    clearBtn.config(state = 'disabled')
    delEntBtn.config(state = 'disabled')
    findBtn.config(state = 'normal')

#This method deletes an asset with asset name assetNameDeleteEnt from the assets table
# and inserts it into the deprecated table
def delete():

    if check_internet():
        global currentUser

        if validateInput((assetNameEditEnt.get())):
            messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                   '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
        elif assetNameEditEnt.get().strip() != '':

            SQLC = '''
                    SELECT * FROM assets
                    WHERE asset_name = \"''' + assetNameEditEnt.get() + '''\";
                '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()

            if tmp:

                MB = messagebox.askquestion('Delete ' + assetNameEditEnt.get() + '?', 'Do you really want to delete '\
                                            + assetNameEditEnt.get() + '?')
                if MB == 'yes':

                    tmp = tmp[0]

                    SQLC = '''
                        SELECT * FROM deprecated
                        WHERE asset_name = \"''' + assetNameEditEnt.get() + '''\";
                    '''
                    crsr.execute(SQLC)
                    temp = crsr.fetchall()

                    if not temp:

                        SQLC = '''
                            UPDATE assets
                            SET
                                last_editor = \"''' + currentUser + '-' + os.environ['COMPUTERNAME'] + '''\",
                                last_editat = \"''' + getTimeDate() + '''\"
                            WHERE asset_name = \"''' + tmp[0] + '''\";
                        '''
                        crsr.execute(SQLC)
                        connection.commit()
                        insertIntoTable(tmp, 'deprecated')
                    else:

                        SQLC = '''
                        UPDATE deprecated
                        SET
                            asset_tag = \"''' + tmp[1] + '''\",
                            serial_num = \"''' + tmp[2] + '''\",
                            model = \"''' + tmp[3] + '''\",
                            category = \"''' + tmp[4] + '''\",
                            status = \"''' + tmp[5] + '''\",
                            location = \"''' + tmp[6] + '''\",
                            date_bought = \"''' + tmp[7] + '''\",
                            make = \"''' + tmp[8] + '''\",
                            notes = \"''' + tmp[9] + '''\",
                            last_editor = \"''' + currentUser + '-' + os.environ['COMPUTERNAME'] + '''\",
                            last_editat = \"''' + getTimeDate() + '''\"
                        WHERE asset_name = \"''' + tmp[0] + '''\";
                        '''
                        crsr.execute(SQLC)
                        connection.commit()

                    SQLC = '''
                        DELETE FROM assets
                        WHERE asset_name = \"''' + assetNameEditEnt.get() + '''\"; 
                        '''
                    messagebox.showinfo('Delete Successful', assetNameEditEnt.get() + ' Successfully Removed')
                    crsr.execute(SQLC)
                    clearEdit()
                    clearSearch()
                    connection.commit()
                    clearEdit()
            else:
                messagebox.showinfo('Incorrect', 'Asset \"' + assetNameEditEnt.get() + '\" does not exist\nPlease try again')

#This method is a shortcut to clear all the Entry fields in the searchTab
def clearSearch():

    textSearchOne.config(state = 'normal')
    textSearchTwo.config(state = 'normal')
    textSearchZero.config(state = 'normal')
    textSearchZero2.config(state = 'normal')
    textSearchOne.delete('1.0', END)
    textSearchTwo.delete('1.0', END)
    textSearchZero.delete('1.0', END)
    textSearchZero2.delete('1.0', END)
    assetNameSearchEnt.delete(0, END)
    assetTagSearchEnt.delete(0, END)
    serialNumSearchEnt.delete(0, END)
    modelSearchEnt.delete(0, END)
    catSearchEnt.delete(0, END)
    statusSearchCombo.delete(0, END)
    locationSearchEnt.delete(0, END)
    makeSearchEnt.delete(0, END)
    noteSearchEnt.delete(0, END)
    dBoughtSearchEnt.config(text = 'Choose Date')
    textSearchOne.config(state='disabled')
    textSearchTwo.config(state='disabled')
    textSearchZero.config(state='disabled')
    textSearchZero2.config(state='disabled')

#This method handles all the login window functions including loging in, creating users, and deleting users
def logout():

    def enterHit(event):

        currentTabLogin = loginTabControl.tab(loginTabControl.select(), "text")
        if currentTabLogin == 'Login':
            login()
        elif currentTabLogin == 'Create User':
            register()
        elif currentTabLogin == 'Delete User':
            deleteAccount()
        elif currentTabLogin == 'Modify User':
            passChange()

    def checkForUser(name):

        SQLC = '''
            SELECT * FROM logins
            WHERE usr_name = \"''' + name.strip() + '''\";
        '''

        crsr.execute(SQLC)
        tmp = crsr.fetchall()
        if tmp:
            return True
        else:
            return False

    def validateUser(name, passw):

        hasher = hashlib.sha256()
        SQLC = '''
            SELECT password FROM logins
            WHERE usr_name = \"''' + name.strip() + '''\";
        '''
        crsr.execute(SQLC)
        tmp = crsr.fetchall()
        hasher.update(bytes(passw, encoding='utf-8'))

        if not tmp:
            return False
        else:
            tmp = tmp[0][0]

        return str(hasher.hexdigest()).strip() == tmp.strip()

    def createUser(name, passw):

        hasher = hashlib.sha256()
        hasher.update(bytes(passw, encoding='utf-8'))
        if not checkVar.get():
            SQLC = '''
                        INSERT INTO logins VALUES(\"''' + name.strip() + '''\", \"''' + str(hasher.hexdigest()) + \
                   '''\", \"offline\", ''' + '0' + ''');
                    '''
        elif checkVar.get():
            SQLC = '''
                        INSERT INTO logins VALUES(\"''' + name.strip() + '''\", \"''' + str(hasher.hexdigest()) + \
                   '''\", \"offline\", ''' + '1' + ''');
            '''
        else:
            SQLC = '''
                INSERT INTO logins VALUES(\"''' + name.strip() + '''\", \"''' + str(hasher.hexdigest()) +\
                '''\", \"offline\", ''' + str(checkVar.get()) + ''');
            '''
        crsr.execute(SQLC)
        connection.commit()

    def login():

        if check_internet():

            updateStatus()
            updateCat()

            if validateInput(userNameEnt.get()) or validateInput(passwordEnt.get()):
                messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                   '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
            elif validateUser(userNameEnt.get(), passwordEnt.get()):

                window.title('EIN - ' + str(userNameEnt.get()))
                global currentUser
                currentUser = userNameEnt.get()

                tabControl.tab(2, state = 'normal')
                tabControl.tab(0, state = 'normal')
                pushBtn.config(state = 'normal')
                delBtn.config(state = 'normal')
                finisBtn.config(state = 'normal')
                rootMenu.entryconfig('Tools', state = 'normal')
                tabControl.select(0)

                try:
                    rootMenu.delete('Developer Tools')
                except TclError:
                    pass
                if currentUser == 'admin':
                    devTMenu = Menu(rootMenu, tearoff=False)
                    tableMenu = Menu(devTMenu, tearoff = False)
                    rootMenu.add_cascade(label='Developer Tools', menu=devTMenu)
                    devTMenu.add_cascade(label='Table Tools', menu=tableMenu)
                    tableMenu.add_command(label='Create A-Table', command=createTable)
                    tableMenu.add_command(label='Drop A-Table', command=dropTable)
                    tableMenu.add_command(label='Print A-Table', command=printTable)
                    tableMenu.add_separator()
                    tableMenu.add_command(label='Create D-Table', command=createDepTable)
                    tableMenu.add_command(label='Drop D-Table', command=dropDepTable)
                    tableMenu.add_command(label='Print D-Table', command=printDepTable)
                    tableMenu.add_separator()
                    tableMenu.add_command(label='Create L-Table', command=createLoginTable)
                    tableMenu.add_command(label='Drop L-Table', command=dropLoginTable)
                    tableMenu.add_command(label='Print L-Table', command=printLoginTable)
                    tableMenu.add_separator()
                    tableMenu.add_command(label='Create S-Table', command=createStatusTable)
                    tableMenu.add_command(label='Drop S-Table', command=dropStatusTable)
                    tableMenu.add_command(label='Print S-Table', command=printStatusTable)
                    tableMenu.add_separator()
                    tableMenu.add_command(label='Create C-Table', command=createCatTable)
                    tableMenu.add_command(label='Drop C-Table', command=dropCatTable)
                    tableMenu.add_command(label='Print C-Table', command=printCatTable)
                    devTMenu.add_command(label = 'Print Window Size', command = printWindowSize)
                    devTMenu.add_command(label = 'Date and Time', command = printTimeDate)
                    devTMenu.add_command(label = 'View Active Users', command = view_active_logins)
                    devTMenu.add_command(label = 'Force Logout User', command = forceLogout)
                    devTMenu.add_command(label = 'Kill All SQL Processes', command = killAllProcesses)
                elif isUserGuest(currentUser):
                    tabControl.tab(2, state='disabled')
                    tabControl.tab(0, state = 'disabled')
                    pushBtn.config(state='disabled')
                    delBtn.config(state='disabled')
                    finisBtn.config(state='disabled')
                    rootMenu.entryconfig('Tools', state='disabled')
                    tabControl.select(1)
                loginWindow.destroy()
                window.deiconify()
                window.lift()

                SQLC = '''
                    UPDATE logins
                    SET
                        status = \"online\"
                    WHERE usr_name = \"''' + currentUser + '''\";
                '''
                crsr.execute(SQLC)
                connection.commit()

                if lastUser != currentUser:
                    clearSearch()
                    clearEdit()
                    tabControl.select(insertionTab)
                    assetName.delete(0, END)
                    assetTag.delete(0, END)
                    serialNum.delete(0, END)
                    model.delete(0, END)
                    cat.delete(0, END)
                    status.delete(0, END)
                    location.delete(0, END)
                    make.delete(0, END)
                    dBought.config(text='Choose Date')
                    notesBtn.config(text='Insert Notes')
                    text.config(state='normal')
                    text.delete('1.0', END)
                    text.config(state='disabled')
            else:
                messagebox.showinfo('Invalid Login', 'Username or Password not correct\nPlease try again')
                passwordEnt.delete(0, END)

    def register():

        if check_internet():
            if validateInput(userNameEnt2.get()) or validateInput(passwordEnt2.get())\
                or validateInput(adminPasswordEnt2.get()):
                messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                       '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
            elif checkForUser(userNameEnt2.get()):
                messagebox.showinfo('Name Already Exists', 'Username Already Exists\nTry Logging In')
            elif len(userNameEnt2.get().strip()) == 0:
                messagebox.showinfo('Input Field Error', 'Please enter a username')
            elif len(userNameEnt2.get().strip()) > 12:
                messagebox.showinfo('Input Field Error', 'Username must be under 12 characters')
            elif len(passwordEnt2.get().strip()) < 8:
                messagebox.showinfo('Input Field Error', 'Password must be eight (8) characters or longer')
            else:

                SQLC = '''
                    SELECT password FROM logins
                    WHERE usr_name = 'admin'
                '''

                crsr.execute(SQLC)
                tmp = crsr.fetchall()[0][0]
                hasher = hashlib.sha256()
                hasher.update(bytes(adminPasswordEnt2.get(), encoding='utf-8'))

                if str(hasher.hexdigest()) == tmp:
                    createUser(userNameEnt2.get(), passwordEnt2.get())
                    messagebox.showinfo('User Created', 'User Account has been created')
                    userNameEnt2.delete(0, END)
                    passwordEnt2.delete(0, END)
                    adminPasswordEnt2.delete(0, END)
                else:
                    messagebox.showinfo('Incorrect', 'Admin Password Incorrect\nPlease Try Again')
                    adminPasswordEnt2.delete(0, END)

    def close():

        on_closing()

    def deleteAccount():

        if check_internet():
            if validateInput(userNameEnt3.get()) or validateInput(adminPasswordEnt.get()):
                messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                       '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
            elif userNameEnt3.get().strip() == 'admin':
                messagebox.showinfo('Failed', 'admin cannot be deleted')
            elif len(userNameEnt3.get().strip()) == 0:
                messagebox.showinfo('Input Field Error', 'Please Input A Username')
            elif checkForUser(userNameEnt3.get().strip()):

                SQLC = '''
                            SELECT password FROM logins
                            WHERE usr_name = 'admin';
                        '''
                crsr.execute(SQLC)
                tmp = crsr.fetchall()[0][0]
                hasher = hashlib.sha256()
                hasher.update(bytes(adminPasswordEnt.get(), encoding='utf-8'))

                if str(hasher.hexdigest()) == tmp:

                    SQLC = '''
                        DELETE FROM logins
                        WHERE usr_name = \"''' + userNameEnt3.get().strip() + '''\";
                        '''
                    crsr.execute(SQLC)
                    connection.commit()
                    messagebox.showinfo('Success', userNameEnt3.get().strip() + ' has been deleted')
                    userNameEnt3.delete(0, END)
                else:
                    messagebox.showinfo('Incorrect', 'Admin Password Incorrect\nPlease Try Again')
            else:
                messagebox.showinfo('User Not Found', 'User ' + userNameEnt3.get().strip() + ' does not exist')
            adminPasswordEnt.delete(0, END)

    def nop():
        pass

    def passChange():

        if check_internet():

            if validateInput(userNameEnt4.get()) or validateInput(oldPasswordEnt.get())\
                or validateInput(newPasswordEnt.get()):
                messagebox.showinfo('Character Error', 'Entries cannot contain the following SQL operators:\n'
                                                       '||, -, *, /, <>, <, >, ,(comma), =, <=, >=, ~=, !=, ^=, (, ), :, ;')
            elif len(userNameEnt4.get().strip()) == 0:
                messagebox.showinfo('Input Field Error', 'Please Enter A Username')
            elif len(oldPasswordEnt.get().strip()) == 0:
                messagebox.showinfo('Input Field Error', 'Please Enter Your Old Password')
            elif len(newPasswordEnt.get().strip()) == 0:
                messagebox.showinfo('Input Field Error', 'Please Enter A New Password')
            else:

                SQLC = '''
                    SELECT * FROM logins
                    WHERE usr_name = \"''' + userNameEnt4.get() + '''\";
                '''
                crsr.execute(SQLC)
                tmp = crsr.fetchall()

                if not tmp:
                    messagebox.showinfo('Input Field Error', 'User Does Not Exist\nTry Using Create User')
                else:
                    SQLC = '''
                        SELECT password FROM logins
                        WHERE usr_name = \"''' + userNameEnt4.get() + '''\";
                    '''
                    crsr.execute(SQLC)
                    tmp = crsr.fetchall()[0][0]
                    hasher = hashlib.sha256()
                    hasher.update(bytes(oldPasswordEnt.get(), encoding='utf-8'))

                    SQLC = '''
                        SELECT password FROM logins
                        WHERE usr_name = \"admin\";
                    '''
                    crsr.execute(SQLC)
                    tmp2 = crsr.fetchall()[0][0]

                    if newPasswordEnt.get() == oldPasswordEnt.get():
                        messagebox.showinfo('Same Password', 'New Password Must Differ From Old Password\nPlease Try Again')
                    elif tmp == hasher.hexdigest() or tmp2 == hasher.hexdigest():

                        hasher = hashlib.sha256()
                        hasher.update(bytes(newPasswordEnt.get(), encoding = 'utf-8'))

                        SQLC = '''
                            UPDATE logins
                            SET
                                password = \"''' + hasher.hexdigest() + '''\"
                            WHERE usr_name = \"''' + userNameEnt4.get() + '''\";
                        '''
                        crsr.execute(SQLC)
                        connection.commit()
                        messagebox.showinfo('Success', userNameEnt4.get() + '\'s Password Has Been Changed')
                        userNameEnt4.delete(0, END)
                    else:
                        messagebox.showinfo('Incorrect Password', 'Old Password Incorrect\nPlease Try Again')
                    oldPasswordEnt.delete(0, END)
                    newPasswordEnt.delete(0, END)

    global currentUser
    global lastUser

    try:
        if checkForUser(currentUser):
            SQLC = '''
                UPDATE logins
                SET
                    status = \"offline\"
                WHERE usr_name = \"''' + currentUser + '''\";
            '''
            crsr.execute(SQLC)
            connection.commit()
    except NameError:
        pass

    lastUser = currentUser
    currentUser = ''

    window.withdraw()
    loginWindow = Toplevel()
    loginWindow.title('Login')
    center(loginWindow)
    loginWindow.geometry('350x250')
    loginWindow.bind('<Return>', enterHit)
    loginWindow.protocol("WM_DELETE_WINDOW", on_closing)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    loginWindow.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    loginWindow.lift()

    # Notebook
    loginTabControl = Notebook(loginWindow)
    loginTab = Frame(loginTabControl)
    registerTab = Frame(loginTabControl)
    deleteTab = Frame(loginTabControl)
    modTab = Frame(loginTabControl)
    loginTabControl.add(loginTab, text='Login')
    loginTabControl.add(registerTab, text='Create User')
    loginTabControl.add(deleteTab, text='Delete User')
    loginTabControl.add(modTab, text = 'Modify User')
    loginTabControl.pack(expand=2, fill='both')

    # Labels
    userNameLabel = Label(loginTab, text='Username: ', font=('Courier', 15))
    passwordLabel = Label(loginTab, text='Password: ', font=('Courier', 15))
    adminPasswordLabel2 = Label(registerTab, text='Admin Password: ', font=('Courier', 15))
    userNameLabel2 = Label(registerTab, text='Username: ', font=('Courier', 15))
    passwordLabel2 = Label(registerTab, text='User Password: ', font=('Courier', 15))
    userNameLabel3 = Label(deleteTab, text='Username: ', font=('Courier', 15))
    adminPasswordLabel = Label(deleteTab, text='Admin Password: ', font=('Courier', 15))
    userNameLabel4 = Label(modTab, text = 'Username: ', font=('Courier', 15))
    oldPasswordLabel = Label(modTab, text = 'Old Password: ', font=('Courier', 15))
    newPasswordLabel = Label(modTab, text = 'New Password: ', font=('Courier', 15))

    # Entries
    userNameEnt = Entry(loginTab, width = 10, font=('Courier', 15))
    passwordEnt = Entry(loginTab, width = 10, show = '*', font=('Courier', 15))
    userNameEnt2 = Entry(registerTab, width = 10, font=('Courier', 15))
    passwordEnt2 = Entry(registerTab, width = 10, show = '*', font=('Courier', 15))
    adminPasswordEnt2 = Entry(registerTab, width = 10, show = '*', font=('Courier', 15))
    userNameEnt3 = Entry(deleteTab, width = 10, font=('Courier', 15))
    adminPasswordEnt = Entry(deleteTab, width = 10, show = '*', font=('Courier', 15))
    userNameEnt4 = Entry(modTab, width = 10, font=('Courier', 15))
    oldPasswordEnt = Entry(modTab, width = 10, show = '*', font=('Courier', 15))
    newPasswordEnt = Entry(modTab, width = 10, show = '*', font=('Courier', 15))

    #Checkbutton
    checkVar = BooleanVar()
    checkVar.set(False)
    checkBox = Checkbutton(registerTab, text = "Guest Account", variable = checkVar)

    # Buttons
    loginEnterBtn = Button(loginTab, text='Login', command=login)
    registerBtn = Button(registerTab, text='Register', command=register)
    closeBtn = Button(loginTab, text='Close', command=close)
    closeBtn2 = Button(registerTab, text='Close', command=close)
    deleteUserBtn = Button(deleteTab, text='Delete Account', command=deleteAccount)
    closeBtn3 = Button(deleteTab, text='Close', command=close)
    changePasswordBtn = Button(modTab, text = 'Change Password', command = passChange)
    closeBtn4 = Button(modTab, text = 'Close', command = close)

    # Grid Building
    userNameLabel.grid(row=0, column=0, pady=5, sticky = N+S)
    userNameEnt.grid(row=0, column=1, padx = 5, pady=5, sticky = E+W)
    passwordLabel.grid(row=1, column=0, pady=5, sticky = N+S)
    passwordEnt.grid(row=1, column=1, pady=5, padx = 5, sticky = E+W)
    loginEnterBtn.grid(row=2, column=0, padx = 5, pady=5, sticky = E+W)
    closeBtn.grid(row=2, column=1, padx = 5, pady=5, sticky = E+W)
    for x in range(0,3):
        Grid.rowconfigure(loginTab, x, weight=1)
    for y in range(0,2):
        Grid.columnconfigure(loginTab, y, weight = 1)

    userNameLabel2.grid(row=0, column=0, pady=5, sticky = N+S)
    userNameEnt2.grid(row=0, column=1, pady=5, padx = 5, sticky = E+W)
    passwordLabel2.grid(row=1, column=0, pady=5, sticky = N+S)
    passwordEnt2.grid(row=1, column=1, padx = 5, pady=5, sticky = E+W)
    adminPasswordLabel2.grid(row=2, column=0, pady=5, sticky = N+S)
    adminPasswordEnt2.grid(row=2, column=1, padx = 5, pady=5, sticky = E+W)
    checkBox.grid(row = 3, column = 0, columnspan = 2, sticky = N+S, padx = 5, pady = 5)
    registerBtn.grid(row=4, column=0, padx=5, pady=5, sticky = E+W)
    closeBtn2.grid(row=4, column=1, padx=5, pady=5, sticky = E+W)
    for x in range(0,5):
        Grid.rowconfigure(registerTab, x, weight=1)
    for y in range(0,2):
        Grid.columnconfigure(registerTab, y, weight = 1)

    userNameLabel3.grid(row=0, column=0, padx=5, pady=5, sticky = N+S)
    userNameEnt3.grid(row=0, column=1, padx=5, pady=5, sticky = E+W)
    adminPasswordLabel.grid(row=1, column=0, padx=5, pady=5, sticky = N+S)
    adminPasswordEnt.grid(row=1, column=1, padx=5, pady=5, sticky = E+W)
    deleteUserBtn.grid(row=2, column=0, padx=5, pady=5, sticky = E+W)
    closeBtn3.grid(row=2, column=1, padx=5, pady=5, sticky = E+W)
    for x in range(0,3):
        Grid.rowconfigure(deleteTab, x, weight=1)
    for y in range(0,2):
        Grid.columnconfigure(deleteTab, y, weight = 1)

    userNameLabel4.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S)
    userNameEnt4.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = E+W)
    oldPasswordLabel.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = N+S)
    oldPasswordEnt.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = E+W)
    newPasswordLabel.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = N+S)
    newPasswordEnt.grid(row = 2, column= 1, padx = 5, pady = 5, sticky = E+W)
    changePasswordBtn.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = E+W)
    closeBtn4.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = E+W)
    for x in range(0,4):
        Grid.rowconfigure(modTab, x, weight=1)
    for y in range(0,2):
        Grid.columnconfigure(modTab, y, weight = 1)

#This method handles all the window display functions for displaying the deprecated assets table
def deprRelease():

    if check_internet():
        global depSearchResults
        depSearchResults = {}

        def clearDepTable():

            MB = messagebox.askquestion('Are you sure?', 'Are you sure you want to delete all assets?'
                                                         '\nThis cannot be undone')
            if MB == 'yes':
                dropDepTable()
                createDepTable()
                deprRelease()
                deprecatedDisplay.destroy()
            else:
                deprecatedDisplay.lift()

        def notesSearch(event):

            global currentNotesDepr
            index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))

            SQLC = '''
                SELECT notes FROM deprecated
                WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
            '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()
            tmp = tmp[0][0]

            tmpRoot = Toplevel()
            tmpRoot.title('Notes For ' + depSearchResults[str(index)])
            tmpRoot.grab_set()
            tmpRoot.geometry('350x350')
            icondata = base64.b64decode(icon)
            tempFile = "icon.ico"
            iconfile = open(tempFile, "wb")
            iconfile.write(icondata)
            iconfile.close()
            tmpRoot.wm_iconbitmap(tempFile)
            os.remove(tempFile)

            textContainerNotes = Frame(tmpRoot, borderwidth=1, relief='sunken')
            textNotes = Text(textContainerNotes, font=('Courier', 10), width=30, height=30, wrap='none', borderwidth=0)
            textVsbNotes = Scrollbar(textContainerNotes, orient="vertical", command=textNotes.yview)
            textHsbNotes = Scrollbar(textContainerNotes, orient="horizontal", command=textNotes.xview)
            textNotes.configure(yscrollcommand=textVsbNotes.set, xscrollcommand=textHsbNotes.set, state='disabled')
            textNotes.grid(row=0, column=0, sticky=N + S + W + E)
            textVsbNotes.grid(row=0, column=1, sticky=N + S + W + E)
            textHsbNotes.grid(row=1, column=0, sticky=N + S + W + E)
            for x in range(1):
                Grid.rowconfigure(textContainerNotes, x, weight=1)
            Grid.columnconfigure(textContainerNotes, 0, weight=1)
            Grid.columnconfigure(textContainerNotes, 1, weight=0)
            textNotes.config(state = 'normal')
            textNotes.insert('1.0', tmp)
            textNotes.config(state='disabled')

            #Grid Building
            textContainerNotes.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
            Grid.rowconfigure(tmpRoot, 0, weight = 1)
            Grid.columnconfigure(tmpRoot, 0, weight = 1)

        def revive(event):

            index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))

            SQLC = '''
                SELECT * FROM deprecated
                WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                '''
            crsr.execute(SQLC)
            temp = crsr.fetchall()
            temp = temp[0]

            MB = messagebox.askquestion('Revive Asset', 'Would you like to revive ' + depSearchResults[str(index)] + '?')
            if MB == 'yes':
                SQLC = '''
                    SELECT * FROM assets
                    WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                '''
                crsr.execute(SQLC)
                if crsr.fetchall():
                    MB2 = messagebox.askquestion('Cannot Revive', 'Another asset under the same name exists '
                                                                  'already\nWould you like to replace current asset?')
                    if MB2 == 'yes':
                        SQLC = '''
                            DELETE FROM assets
                            WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                        '''
                        crsr.execute(SQLC)
                        connection.commit()
                        insertIntoTable(temp, 'assets')
                        clearSearch()

                        SQLC = '''
                            UPDATE assets
                            SET
                                last_editor = \"''' + currentUser + '''\",
                                last_editat = \"''' + getTimeDate() + '''\"
                            WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                        '''
                        crsr.execute(SQLC)
                        connection.commit()
                    else:
                        return
                else:
                    insertIntoTable(temp, 'assets')
                    SQLC = '''
                        UPDATE assets
                        SET
                            last_editor = \"''' + currentUser + '''\",
                            last_editat = \"''' + getTimeDate() + '''\"
                        WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                    '''
                    crsr.execute(SQLC)
                    connection.commit()
                    clearSearch()
                SQLC = '''
                    DELETE FROM deprecated
                    WHERE asset_name = \"''' + depSearchResults[str(index)] + '''\";
                '''
                crsr.execute(SQLC)
                connection.commit()
                deprecatedDisplay.destroy()
                deprRelease()

        #Initial Setup
        global currentUser
        deprecatedDisplay = Toplevel()
        deprecatedDisplay.title('E.I.N. Deprecated Assets - ' + currentUser)
        depRootMenu = Menu(deprecatedDisplay)
        depFileMenu = Menu(depRootMenu, tearoff = False)
        depRootMenu.add_cascade(label = 'Options', menu = depFileMenu)
        depFileMenu.add_command(label = 'Clear Deprecated Table', command = clearDepTable)
        deprecatedDisplay.config(menu=depRootMenu)
        global icon
        icondata = base64.b64decode(icon)
        tempFile = "icon.ico"
        iconfile = open(tempFile, "wb")
        iconfile.write(icondata)
        iconfile.close()
        deprecatedDisplay.wm_iconbitmap(tempFile)
        os.remove(tempFile)
        deprecatedDisplay.lift()

        #Text Display
        deprTextContainer = Frame(deprecatedDisplay, borderwidth=1, relief='sunken')
        deprText = Text(deprTextContainer, font=('Courier', 10), width=75, height=14, wrap='none', borderwidth=0)
        deprTextVsb = Scrollbar(deprTextContainer, orient="vertical", command=deprText.yview)
        deprTextHsb = Scrollbar(deprTextContainer, orient="horizontal", command=deprText.xview)
        deprText.configure(yscrollcommand=deprTextVsb.set, xscrollcommand=deprTextHsb.set)
        deprText.config(state='disabled')
        deprText.grid(row=0, column=2, sticky="nsew")
        deprTextVsb.grid(row=0, column=3, sticky="ns")
        deprTextHsb.grid(row=1, column=2, sticky="ew")

        crsr.execute('SELECT * FROM deprecated')
        tmp = crsr.fetchall()
        tmp.sort()

        deprText.config(state='normal')
        for i in tmp:
            for j in range(len(i)):
                if j == 0 and not isUserGuest(currentUser):
                    tag = 'depSearch' + i[j]
                    depSearchResults[str(len(depSearchResults) + 3)] = i[j]
                    deprText.tag_config(str(tag), foreground = 'blue')
                    deprText.tag_bind(tag, '<Button-1>', lambda e:revive(e))
                    deprText.insert(END, stringGridFormat(i[j]), tag)
                    deprText.insert(END, '|')
                elif j == 0 and isUserGuest(currentUser):
                    depSearchResults[str(len(depSearchResults) + 3)] = i[j]
                    deprText.insert(END, stringGridFormat(i[j]) + '|')
                elif j == 9:
                    tag = 'searchNotesDepr' + str(j)
                    deprText.tag_config(str(tag), foreground='blue')
                    deprText.tag_bind(tag, '<Button-1>', lambda e: notesSearch(e))
                    deprText.insert(END, stringGridFormat('notes'), tag)
                    deprText.insert(END, '|')
                elif j+1 == len(i):
                    deprText.insert(END, stringGridFormat(i[j]))
                else:
                    deprText.insert(END, stringGridFormat(i[j]) + '|')
            deprText.insert(END, '\n')

        deprText.insert('1.0', '--------------------\n')
        for i in range(0,13):
            deprText.insert('1.0', '--------------------' + '|')
        deprText.insert('1.0', '\n')
        deprText.insert('1.0', stringGridFormat('Deleted At'))
        deprText.insert('1.0', stringGridFormat('Deleted By') + '|')
        deprText.insert('1.0', stringGridFormat('Created At') + '|')
        deprText.insert('1.0', stringGridFormat('Created By') + '|')
        deprText.insert('1.0', stringGridFormat('Notes') + '|')
        deprText.insert('1.0', stringGridFormat('Date Bought') + '|')
        deprText.insert('1.0', stringGridFormat('Location') + '|')
        deprText.insert('1.0', stringGridFormat('Status') + '|')
        deprText.insert('1.0', stringGridFormat('Category') + '|')
        deprText.insert('1.0', stringGridFormat('Model') + '|')
        deprText.insert('1.0', stringGridFormat('Make') + '|')
        deprText.insert('1.0', stringGridFormat('Serial Number') + '|')
        deprText.insert('1.0', stringGridFormat('Asset Tag') + '|')
        deprText.insert('1.0', stringGridFormat('Asset Name') + '|')
        deprText.config(state = 'disabled')

        #Grid Building
        deprTextContainer.grid(row = 0, column = 0, sticky = N+S+E+W)
        Grid.rowconfigure(deprecatedDisplay, 0, weight = 1)
        Grid.columnconfigure(deprecatedDisplay, 0, weight = 1)

#This method Prints the window size
def printWindowSize():

    print(window.winfo_width())
    print(window.winfo_height())

#This method returns the System Time and Date
def getTimeDate():
    return str(dt.datetime.now())[0:-10]

#This method returns the System Time and Date
def printTimeDate():
    print(getTimeDate())

#This method handles all the window display functions for displaying a calendar
# and sets the text of btn to the specified date
def chooseDate(btn):

    global icon
    def confirm():

        btn.config(text = cal.get_date())
        calRoot.grab_release()
        calRoot.destroy()

    def cancel():

        calRoot.grab_release()
        calRoot.destroy()

    def removeDate():
        btn.config(text = 'Choose Date')
        calRoot.grab_release()
        calRoot.destroy()

    calRoot = Toplevel()
    center(calRoot)
    calRoot.geometry('300x300')
    calRoot.title('Choose a Date')
    calRoot.grab_set()
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    calRoot.wm_iconbitmap(tempFile)
    os.remove(tempFile)

    #Buttons
    confirmBtn = Button(calRoot, text = 'Confirm', command = confirm)
    cancelBtn = Button(calRoot, text = 'Cancel', command = cancel)
    removeBtn = Button(calRoot, text = 'Remove Date', command = removeDate)

    #Calendar
    cal = Calendar(calRoot, firstweekday = 'sunday')
    cal.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
    cancelBtn.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    removeBtn.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
    confirmBtn.grid(row = 2, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
    Grid.rowconfigure(calRoot, 0, weight = 1)
    for y in range(2):
        Grid.columnconfigure(calRoot, y, weight = 1)

#This method displays all information about EIN
def about():

    aboutRoot = Toplevel()
    aboutRoot.title('About EIN')
    aboutRoot.geometry('250x150')
    aboutRoot.resizable(width=False, height=False)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    aboutRoot.wm_iconbitmap(tempFile)
    os.remove(tempFile)

    #Labels
    nameLabel = Label(aboutRoot, text = 'Electronics Inventory Notetaker (EIN)')
    authorLabel = Label(aboutRoot, text = 'Author: Spencer Gray')
    akLabel = Label(aboutRoot, text = '')
    versionLabel = Label(aboutRoot, text = 'Version: ' + version)

    #Buttons
    closeBtn = Button(aboutRoot, text = 'Close', command = aboutRoot.destroy)

    #Grid Building
    nameLabel.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = E+W)
    versionLabel.grid(row=1, column=0, padx=5, pady=5, sticky = E+W)
    authorLabel.grid(row=2, column=0, padx=5, pady=5, sticky = E+W)
    akLabel.grid(row=3, column=0, padx=5, pady=5, sticky = E+W)
    closeBtn.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = N+S)
    for x in range(0,4):
        Grid.rowconfigure(aboutRoot, x, weight = 1)
    Grid.columnconfigure(aboutRoot, 0, weight = 1)

#This method exists so that the exe compiler does not exclude the babel library import
# this method has no actual function
def nop():
    print(babel.__version__)
    print(babel.numbers.date_)

#This method checks if word contains MySQL operators
def validateInput(word):

    return '\"' in word or '\'' in word or '||' in word or '*' in word or '/' in word or '<' in word or '>' in word\
        or ',' in word or '=' in word or '~=' in word or '!=' in word or '^=' in word or '(' in word or ')' in word\
        or ':' in word or ';' in word

#This method binds the return key on the keyboard to some functions within the program
def onEnterHit(event):

    currentTab = tabControl.tab(tabControl.select(), "text")

    if currentTab == 'Insert':
        pass
    elif currentTab == 'Search':
        search()
    elif currentTab == 'Edit / Delete':

        if str(findBtn['state']) == 'normal':
            findAsset()
        else:
            update()

#This method creates a window with a text editor for note editing
#   notes are any imported strings to be added to the text box
#   export determines which tab is being worked on (insert tab or edit tab)
#   btn is the button that triggered the note editing event
def notesEditor(notes, export, btn):

    def confirm():

        if export == 'insert':
            global currentNotesInsert
            currentNotesInsert = textNotes.get('1.0', END)
            btn.config(text=currentNotesInsert[0:6].strip() + '...')
        elif export == 'edit':
            global currentNotesEdit
            currentNotesEdit = textNotes.get('1.0', END)
            btn.config(text=currentNotesEdit[0:6].strip() + '...')

        cancel()

    def cancel():
        notesRoot.grab_release()
        notesRoot.destroy()

    def removeNotes():
        if export == 'insert':
            global currentNotesInsert
            currentNotesInsert = ''
        elif export == 'edit':
            global currentNotesEdit
            currentNotesEdit = ''
        btn.config(text = 'Insert Notes')
        textNotes.delete('1.0', END)
        cancel()

    notesRoot = Toplevel()
    notesRoot.title('Note')
    notesRoot.grab_set()
    notesRoot.geometry('350x350')
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    notesRoot.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    center(notesRoot)

    #Buttons
    confirmBtn = Button(notesRoot, text = 'Confirm', command = confirm)
    cancelBtn = Button(notesRoot, text = 'Cancel', command = cancel)
    delNotesBtn = Button(notesRoot, text = 'Delete Notes', command = removeNotes)

    # Text Box
    textContainerNotes = Frame(notesRoot, borderwidth=1, relief='sunken')
    textNotes = Text(textContainerNotes, font=('Courier', 10), width=30, height=30, wrap='none', borderwidth=0)
    textVsbNotes = Scrollbar(textContainerNotes, orient="vertical", command=textNotes.yview)
    textHsbNotes = Scrollbar(textContainerNotes, orient="horizontal", command=textNotes.xview)
    textNotes.configure(yscrollcommand=textVsbNotes.set, xscrollcommand=textHsbNotes.set, state='disabled')
    textNotes.grid(row=0, column=0, sticky=N + S + W + E)
    textVsbNotes.grid(row=0, column=1, sticky=N + S + W + E)
    textHsbNotes.grid(row=1, column=0, sticky=N + S + W + E)
    for x in range(1):
        Grid.rowconfigure(textContainerNotes, x, weight=1)
    Grid.columnconfigure(textContainerNotes, 0, weight=1)
    Grid.columnconfigure(textContainerNotes, 1, weight=0)
    textNotes.config(state = 'normal')
    textNotes.insert('1.0', notes)

    #Grid Building
    confirmBtn.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
    cancelBtn.grid(row = 0, column = 2, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
    delNotesBtn.grid(row = 1, column = 0, columnspan = 4, padx = 5, pady = 5, sticky = N+S+E+W)
    textContainerNotes.grid(row = 2, column = 0, columnspan = 4, padx = 5, pady = 5, sticky = N+S+E+W)
    Grid.rowconfigure(notesRoot, 0, weight = 1)
    Grid.rowconfigure(notesRoot, 1, weight = 1)
    Grid.rowconfigure(notesRoot, 2, weight = 150)
    Grid.columnconfigure(notesRoot, 0, weight = 1)
    Grid.columnconfigure(notesRoot, 1, weight = 1)
    Grid.columnconfigure(notesRoot, 2, weight = 1)
    Grid.columnconfigure(notesRoot, 3, weight = 1)

#This method reconnects the to the database
def reconnect():

    clearSearch()
    url = 'http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)

        global connection
        global crsr
        '''connection = mysql.connector.connect(

            host='192.168.244.20',
            user='graysp',
            passwd='Service6',
            database='AMCassets'
        )'''
        connection = sqlite3.connect('AMC.db')
        crsr = connection.cursor()
    except requests.ConnectionError:
        messagebox.showinfo('Network Error', 'No Internet Connection Available\nPlease Reconnect to Internet')

#This method returns True if the machine is connected to the internet
#   False otherwise
def check_internet():
    url = 'http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)

        try:
            connection
        except NameError:
            messagebox.showinfo('Network Error', 'Not Connected to Database'
                                                 '\nPlease Reconnect Using the \'Tools\' Tab')
            return False
        else:
            return True
    except requests.ConnectionError:
        messagebox.showinfo('Network Error', 'No Internet Connection Available\nPlease Reconnect to Internet')
    return False

#This method centers a window based on screen size
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def on_closing():

    if messagebox.askokcancel('Quit?', 'Do you want to quit the application?'):

        if check_internet():
            global currentUser

            if currentUser.strip() != '':

                SQLC = '''
                    UPDATE logins
                    SET
                        status = \"offline\"
                    WHERE usr_name = \"''' + currentUser + '''\";
                '''

                crsr.execute(SQLC)
                connection.commit()
            connection.close()
        window.destroy()

def view_active_logins():

    valRoot = Toplevel()
    valRoot.title('EIN Users')
    valRoot.grab_set()
    valRoot.geometry('230x260')
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    valRoot.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    center(valRoot)

    #Text Container
    textContainerVAL = Frame(valRoot, borderwidth=1, relief='sunken')
    textVAL = Text(textContainerVAL, font=('Courier', 10), width=75, height=16, wrap='none', borderwidth=0)
    textVsbVAL = Scrollbar(textContainerVAL, orient="vertical", command=textVAL.yview)
    textHsbVAL = Scrollbar(textContainerVAL, orient="horizontal", command=textVAL.xview)
    textVAL.configure(yscrollcommand=textVsbVAL.set, xscrollcommand=textHsbVAL.set)
    textVAL.grid(row=0, column=0, sticky=N + S + E + W)
    textVsbVAL.grid(row=0, column=1, sticky=N + S + E + W)
    textHsbVAL.grid(row=1, column=0, sticky=N + S + E + W)
    Grid.rowconfigure(textContainerVAL, 0, weight=1)
    Grid.columnconfigure(textContainerVAL, 0, weight=1)
    Grid.columnconfigure(textContainerVAL, 1, weight=0)

    #Text Assembling
    SQLC = '''
        SELECT usr_name FROM logins
        WHERE status = \"online\";
    '''
    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    textVAL.insert(END, '----------Online----------\n')
    for line in tmp:
        if isUserGuest(str(line[0])):
            textVAL.insert(END, '  ' + str(line[0]) + ' (guest)\n')
        else:
            textVAL.insert(END, '  ' + str(line[0]) + '\n')

    SQLC = '''
             SELECT usr_name FROM logins
             WHERE status = \"offline\";
         '''
    crsr.execute(SQLC)
    tmp = crsr.fetchall()

    textVAL.insert(END, '\n----------Offline---------\n')
    for line in tmp:

        if isUserGuest(str(line[0])):
            textVAL.insert(END, '  ' + str(line[0]) + '(guest)\n')
        else:
            textVAL.insert(END, '  ' + str(line[0]) + '\n')
    textVAL.config(state = 'disabled')

    #Grid Building
    textContainerVAL.grid(row = 0, column = 0, sticky = N+S+E+W)
    Grid.rowconfigure(valRoot, 0, weight = 1)
    Grid.columnconfigure(valRoot, 0, weight = 1)

def forceLogout():

    def FL(event):
        SQLC = '''
            SELECT * FROM logins
            WHERE usr_name = \"''' + ev.get() + '''\";
        '''
        crsr.execute(SQLC)
        tmp = crsr.fetchall()

        if tmp:
            SQLC = '''
                UPDATE logins
                SET
                    status = \"offline\"
                WHERE usr_name = \"''' + ev.get() + '''\";
            '''
            crsr.execute(SQLC)
            connection.commit()
            messagebox.showinfo('Success', ev.get() + ' successfully logged out')
            close()

        else:
            messagebox.showinfo('User Not Found', 'User was not found\nPlease try again')

    def close():
        root.destroy()

    root = Toplevel()
    root.title('Force User Logout')
    root.grab_set()
    root.geometry('200x75')
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', FL)

    #Entry
    ev = Entry(root, width = 10, font=('Courier', 10))

    #Buttons
    b = Button(root, text='logout', command = lambda: FL(ev))
    c = Button(root, text = 'close', command = close)

    #Label
    l = Label(root, text='User Name: ', font=('Courier', 10))

    #Grid Building
    l.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    ev.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
    b.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
    c.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
    Grid.columnconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 1, weight = 1)

def addStatus():

    def FL(event):

        if len(ev.get().strip()) > 20:
            messagebox.showinfo('Character Limit Reached', ev.get().strip() + ' exceeds the 20 character limit'
                                                                              '\nPlease try again')
        else:

            SQLC = '''
                SELECT * FROM status
                WHERE name = \"''' + ev.get().strip() + '''\";
            '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()

            if tmp:
                messagebox.showinfo('Already Exists', 'Status is already in list')
            else:

                SQLC = '''
                    INSERT INTO status VALUES(\"''' + ev.get().strip() + '''\");
                '''
                crsr.execute(SQLC)
                connection.commit()

                messagebox.showinfo('Success', ev.get().strip() + ' successfully added')
                close()
        updateStatus()

    def close():
        root.destroy()

    root = Toplevel()
    root.title('Add Status')
    root.grab_set()
    root.geometry('200x75')
    root.resizable(width=False, height=False)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', FL)

    #Entry
    ev = Entry(root, width = 10, font=('Courier', 10))

    #Buttons
    b = Button(root, text='Add Status', command = lambda: FL(ev))
    c = Button(root, text = 'Close', command = close)

    #Label
    l = Label(root, text='Status: ', font=('Courier', 10))

    #Grid Building
    l.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    ev.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
    b.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
    c.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
    Grid.columnconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 1, weight = 1)

def updateStatus():

    crsr.execute('SELECT name FROM status')
    tmp = crsr.fetchall()

    status['values'] = tmp
    statusSearchCombo['values'] = tmp
    statusEditCombo['values'] = tmp

def addCat():

    def FL(event):

        if len(ev.get().strip()) > 20:
            messagebox.showinfo('Character Limit Reached', ev.get().strip() + ' exceeds the 20 character limit'
                                                                              '\nPlease try again')
        else:

            SQLC = '''
                SELECT * FROM category
                WHERE name = \"''' + ev.get().strip() + '''\";
            '''
            crsr.execute(SQLC)
            tmp = crsr.fetchall()

            if tmp:
                messagebox.showinfo('Already Exists', 'Category is already in list')
            else:

                SQLC = '''
                    INSERT INTO category VALUES(\"''' + ev.get().strip() + '''\");
                '''
                crsr.execute(SQLC)
                connection.commit()

                messagebox.showinfo('Success', ev.get().strip() + ' successfully added')
                close()
        updateCat()

    def close():
        root.destroy()

    root = Toplevel()
    root.title('Add Category')
    root.grab_set()
    root.geometry('200x75')
    root.resizable(width=False, height=False)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', FL)

    #Entry
    ev = Entry(root, width = 10, font=('Courier', 10))

    #Buttons
    b = Button(root, text='Add Category', command = lambda: FL(ev))
    c = Button(root, text = 'Close', command = close)

    #Label
    l = Label(root, text='Category: ', font=('Courier', 10))

    #Grid Building
    l.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    ev.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
    b.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
    c.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
    Grid.columnconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 1, weight = 1)

def updateCat():

    crsr.execute('SELECT name FROM category')
    tmp = crsr.fetchall()

    cat['values'] = tmp
    catSearchEnt['values'] = tmp
    catEditEnt['values'] = tmp

def removeStatus():

    def FL(event):

        SQLC = '''
            DELETE FROM status
            WHERE name = \"''' + ev.get().strip() + '''\";
        '''
        crsr.execute(SQLC)
        connection.commit()
        messagebox.showinfo('Success', ev.get().strip() + ' successfully removed')
        close()
        updateStatus()

    def close():
        root.destroy()

    root = Toplevel()
    root.title('Remove Status')
    root.grab_set()
    root.geometry('200x75')
    root.resizable(width=False, height=False)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', FL)

    #Entry
    ev = Entry(root, width = 10, font=('Courier', 10))

    #Buttons
    b = Button(root, text='Add Status', command = lambda: FL(ev))
    c = Button(root, text = 'Close', command = close)

    #Label
    l = Label(root, text='Status: ', font=('Courier', 10))

    #Grid Building
    l.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    ev.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
    b.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
    c.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
    Grid.columnconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 1, weight = 1)

def removeCat():

    def FL(event):

        SQLC = '''
            DELETE FROM category
            WHERE name = \"''' + ev.get().strip() + '''\";
        '''
        crsr.execute(SQLC)
        connection.commit()
        messagebox.showinfo('Success', ev.get().strip() + ' successfully removed')
        close()
        updateCat()

    def close():
        root.destroy()

    root = Toplevel()
    root.title('Remove Category')
    root.grab_set()
    root.geometry('200x75')
    root.resizable(width=False, height=False)
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', FL)

    #Entry
    ev = Entry(root, width = 10, font=('Courier', 10))

    #Buttons
    b = Button(root, text='Add Category', command = lambda: FL(ev))
    c = Button(root, text = 'Close', command = close)

    #Label
    l = Label(root, text='Category: ', font=('Courier', 10))

    #Grid Building
    l.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
    ev.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
    b.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
    c.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
    Grid.columnconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 1, weight = 1)

def printWindow():

    def getPrintFormatText():

        def printFormat(word):

            max = 32
            while len(word) < max:
                word = word + ' '
            return word

        global searchResults

        export = ''
        count = 1

        for word in searchResults.values():

            crsr.execute('SELECT * FROM assets WHERE asset_name = \"' + word + '\";')
            tmp = crsr.fetchall()[0]
            export += str('(' + str(count) + ') Asset Name: ' + tmp[0])

            export += '\n\t|' + printFormat('Asset Tag: ' + tmp[1]) + '|' + printFormat('Serial Number: ' + tmp[2])
            export += '\n\t|' + printFormat('Make: ' + tmp[3]) + '|' + printFormat('Model: ' + tmp[4])
            export += '\n\t|' + printFormat('Category: ' + tmp[5]) + '|' + printFormat('Status: ' + tmp[6])
            export += '\n\t|' + printFormat('Location: ' + tmp[7]) + '|' + printFormat('Date Bought: ' + tmp[8])
            export += '\n\t|' + printFormat('Created By: ' + tmp[10]) + '|' + printFormat('Created At: ' + tmp[11])
            export += '\n\t|' + printFormat('Lasted Editor: ' + tmp[12]) + '|' + printFormat('Last Edited At: ' + tmp[13])
            export += '\n\n'

            count += 1

        return export

    def Print():

        # printerNameList[v.get()-1][1]

        tmp = win32print.GetDefaultPrinter()
        win32print.SetDefaultPrinter(printerNameList[v.get() - 1][1])

        filename = tempfile.mktemp(".txt")
        open(filename, "w").write(getPrintFormatText())
        win32api.ShellExecute(
            0,
            "printto",
            filename,
            '"%s"' % win32print.GetDefaultPrinter(),
            ".",
            0
        )

        win32print.SetDefaultPrinter(tmp)
        root.destroy()

    printerNameList = []
    root = Toplevel()
    root.title('Printing Options')
    #root.geometry('267x151')
    root.grab_set()
    icondata = base64.b64decode(icon)
    tempFile = "icon.ico"
    iconfile = open(tempFile, "wb")
    iconfile.write(icondata)
    iconfile.close()
    root.wm_iconbitmap(tempFile)
    os.remove(tempFile)
    root.bind('<Return>', Print)
    printBtn = Button(root, text='Print', command=Print)

    v = IntVar()
    count = 1

    for p in win32print.EnumPrinters(3):
        printerNameList.append((count, p[2]))
        count += 1

    for mode, name in printerNameList:
        b = Radiobutton(root, text=name, variable=v, value=mode)
        b.pack(anchor = W)

    printBtn.pack(fill=BOTH)

    root.mainloop()

def isUserGuest(user):

    SQLC = '''
        SELECT * FROM logins
        WHERE usr_name = \"''' + user + '''\" AND is_guest = 1;
    '''
    crsr.execute(SQLC)

    if crsr.fetchall():
        return True
    else:
        return False

def saveInsertForLater():

    if text.get('1.0', END).strip() != '':

        file = filedialog.asksaveasfile(mode='w', defaultextension=".ein")

        if file is None:
            return

        global insertNotes
        temp = text.get('1.0', END)
        if temp.strip() != '':
            temp = temp.splitlines()
            for i in temp:

                if i.strip() != '':

                    file.write('NL')
                    i = i.split(',')
                    i[9] = insertNotes[int(i[9]) - 1]

                    for word in i:
                        file.write('-' + word + '\n')

        messagebox.showinfo('Saved', 'Save Successful')

def insertSavedData():

    def searchForInsert(event):

        index = math.floor(float(event.widget.index("@%s,%s" % (event.x, event.y))))\

        boxOption = messagebox.askquestion('Remove Asset?', 'Would you like to remove this asset from the list?')

        if boxOption == 'yes':
            text.config(state = 'normal')
            text.delete(str(index) + '.0', str(index + 1) + '.0')
            text.config(state = 'disabled')

    file = filedialog.askopenfilename(filetypes=[("EIN files", "*.ein")])

    if file is None:
        return

    fileIn = open(file)

    global insertNotes
    temp = fileIn.read()
    text.config(state='normal')
    insertNotes = []
    text.delete('1.0', END)
    notesCount = 1
    for tmp in temp.split('NL'):

        j = 0
        newLine = ''
        for i in tmp.split('-'):

            if j == 10:
                insertNotes.append(i)
                newLine += str(notesCount) + ', '
                notesCount += 1
            elif j > 0:
                newLine += str(i.strip() + ', ')
            j += 1
        newLine = newLine[0:-2]
        text.insert(1.0, str(newLine)[int(str(newLine).find(',')):] + '\n')
        tag = 'insert' + str(newLine)[0:int(str(newLine).find(','))]
        text.tag_config(str(tag), foreground='blue')
        text.tag_bind(str(tag), '<Button-1>', lambda e: searchForInsert(e))
        text.insert(1.0, str(newLine)[0:int(str(newLine).find(','))], str(tag))
    text.config(state = 'disabled')

def on_mousewheel(event):

    textSearchOne.yview('scroll', str(int(-1 * event.delta/120)), 'units')
    textSearchTwo.yview('scroll', str(int(-1 * event.delta/120)), 'units')
    return 'break'

def viewall(*args):

    if str(args[0]) == 'moveto' or str(args[0]) == 'scroll':
        global textSearchOne, textSearchTwo
        textSearchOne.yview(*args)
        textSearchTwo.yview(*args)
    else:
        viewall('scroll',str(int(-1*(args[0].delta/120))),'units')

def viewallH(*args):

    if str(args[0]) == 'moveto' or str(args[0]) == 'scroll':
        global textSearchTwo, textSearchZero2
        textSearchTwo.xview(*args)
        textSearchZero2.xview(*args)
    else:
        textSearchTwo.xview('scroll', str(int(-1 * args[0].delta / 120)), 'units')
        textSearchZero2.xview('scroll', str(int(-1 * args[0].delta / 120)), 'units')


def killAllProcesses():
    crsr.execute('SHOW PROCESSLIST')
    for process in crsr.fetchall():
        crsr.execute('KILL ' + str(process[0]))

def removeScrollWheel(event):
    return 'break'

def testCode():

    createTable()
    createDepTable()
    createLoginTable()
    createStatusTable()
    createCatTable()

# ----------------------------Main-------------------------------------
# Initial Setup
window = Tk()
window.withdraw()
window.title('EIN')
windowW = '730'
windowH = '525'
window.geometry(windowW + 'x' + windowH)
center(window)
window.bind('<Return>', onEnterHit)
insertResults = []
currentNotesInsert = ''
currentNotesEdit = ''
insertNotes = []
window.protocol("WM_DELETE_WINDOW", on_closing)
lastUser = ''
currentUser = ''
style = ThemedTk.ThemedStyle(window)
style.set_theme('arc')

#Server
version = '3.2.5'
'''connection = mysql.connector.connect(

    host='192.168.244.20',
    user='graysp',
    passwd='Service6',
    database='AMCassets'
)'''
connection = sqlite3.connect('AMC.db')
crsr = connection.cursor()

#File Menu
rootMenu = Menu(window)
fileMenu = Menu(rootMenu, tearoff = False)
toolsMenu = Menu(rootMenu, tearoff = False)
rootMenu.add_cascade(label = 'File', menu = fileMenu)
rootMenu.add_cascade(label = 'Tools', menu = toolsMenu)
fileMenu.add_command(label = 'View Deprecated Assets', command = deprRelease)
fileMenu.add_command(label = 'View Active Users', command = view_active_logins)
fileMenu.add_command(label = 'About', command = about)
fileMenu.add_command(label = 'Log Out', command = logout)
toolsMenu.add_command(label = 'Reconnect to Server', command = reconnect)
toolsMenu.add_command(label = 'Add Status', command = addStatus)
toolsMenu.add_command(label = 'Remove Status', command = removeStatus)
toolsMenu.add_command(label = 'Add Category', command = addCat)
toolsMenu.add_command(label = 'Remove Category', command = removeCat)
window.config(menu = rootMenu)

# Notebooks
tabControl = Notebook(window)
insertionTab = Frame(tabControl)
tabControl.add(insertionTab, text='Insert')
tabControl.pack(expand=1, fill='both')
searchTab = Frame(tabControl)
tabControl.add(searchTab, text='Search')
tabControl.pack(expand=1, fill='both')
editTab = Frame(tabControl)
tabControl.add(editTab, text = 'Edit / Delete')
tabControl.pack(expand = 1, fill = 'both')

#-----------------------------------Edit Tab-----------------------------------------
#Labels
assetNameEdit = Label(editTab, text='Asset Name: ', font=('Courier', 10))
assetTagEdit = Label(editTab, text='Asset Tag: ', font=('Courier', 10))
serialNumEdit = Label(editTab, text='Serial Number: ', font=('Courier', 10))
modelEdit = Label(editTab, text='Model: ', font=('Courier', 10))
catEdit = Label(editTab, text='Category: ', font=('Courier', 10))
statusEdit = Label(editTab, text='Status: ', font=('Courier', 10))
locationEdit = Label(editTab, text='Location: ', font=('Courier', 10))
dBoughtEdit = Label(editTab, text='Date Bought: ', font=('Courier', 10))
makeEdit = Label(editTab, text = 'Make: ', font=('Courier', 10))
notesEdit = Label(editTab, text = 'Notes: ', font=('Courier', 10))

#Frames
buttonFrameOne = Frame(editTab)
buttonFrameTwo = Frame(editTab)

#Buttons
findBtn = Button(buttonFrameOne, text = 'Find', command = findAsset)
updateBtn = Button(buttonFrameOne, text = 'Update', command = update, state = 'disabled')
clearBtn = Button(buttonFrameTwo, text = 'Cancel', command = clearEdit, state = 'disabled')
delEntBtn = Button(buttonFrameTwo, text = 'Delete', command = delete, state = 'disabled')
dBoughtEditEnt = Button(editTab, text = 'Choose Date', command = lambda: chooseDate(dBoughtEditEnt))
dBoughtEditEnt.config(state = 'disabled')
notesEditBtn = Button(editTab, text = 'Edit Notes', command = lambda: notesEditor(currentNotesEdit, 'edit', notesEditBtn))
notesEditBtn.config(state = 'disabled')

#Entries
assetNameEditEnt = Entry(editTab, width = 10, font=('Courier', 10))
assetTagEditEnt = Entry(editTab, width = 10, font=('Courier', 10))
assetTagEditEnt.config(state = 'disabled')
serialNumEditEnt = Entry(editTab, width = 10, font=('Courier', 10))
serialNumEditEnt.config(state = 'disabled')
modelEditEnt = Entry(editTab, width = 10, font=('Courier', 10))
modelEditEnt.config(state = 'disabled')
locationEditEnt = Entry(editTab, width = 10, font=('Courier', 10))
locationEditEnt.config(state = 'disabled')
makeEditEnt = Entry(editTab, width = 10, font=('Courier', 10), state = 'disabled')

#Combobox
statusEditCombo = Combobox(editTab, width = 8, font=('Courier', 10))
statusEditCombo.config(state = 'disabled')
catEditEnt = Combobox(editTab, width = 10, font=('Courier', 10))
catEditEnt.config(state = 'disabled')

#Grid Layout
assetNameEdit.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = N+S)
assetNameEditEnt.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
assetTagEdit.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = N+S)
assetTagEditEnt.grid(row = 1, column = 3, padx = 5, pady = 5, sticky = N+S+E+W)
serialNumEdit.grid(row = 1, column = 4, padx = 5, pady = 5, sticky = N+S)
serialNumEditEnt.grid(row = 1, column = 5, padx = 5, pady = 5, sticky = N+S+E+W)
makeEdit.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = N+S)
makeEditEnt.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
modelEdit.grid(row = 2, column = 2, padx = 5, pady = 5, sticky = N+S)
modelEditEnt.grid(row = 2, column = 3, padx = 5, pady = 5, sticky = N+S+E+W)
catEdit.grid(row = 2, column = 4, padx = 5, pady = 5, sticky = N+S)
catEditEnt.grid(row = 2, column = 5, padx = 5, pady = 5, sticky = N+S+E+W)
statusEdit.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = N+S)
statusEditCombo.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
locationEdit.grid(row = 3, column = 2, padx = 5, pady = 5, sticky = N+S)
locationEditEnt.grid(row = 3, column = 3, padx = 5, pady = 5, sticky = N+S+E+W)
dBoughtEdit.grid(row = 3, column = 4, padx = 5, pady = 5, sticky = N+S)
dBoughtEditEnt.grid(row = 3, column = 5, padx = 5, pady = 5, sticky = N+S+E+W)
notesEditBtn.grid(row = 4, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
notesEdit.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = N+S)
buttonFrameOne.grid(row = 5, column = 0, columnspan = 3, pady = 5, sticky = N+S+E+W)
buttonFrameTwo.grid(row = 5, column = 3, columnspan = 3, pady = 5, sticky = N+S+E+W)
findBtn.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
updateBtn.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
delEntBtn.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
clearBtn.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
for y in range(0, 2):
    Grid.columnconfigure(buttonFrameOne, y, weight = 1)
    Grid.columnconfigure(buttonFrameTwo, y, weight = 1)
for y in range(7):
    Grid.columnconfigure(editTab, y, weight = 1)
newOrder = (assetNameEditEnt, assetTagEditEnt, serialNumEditEnt, modelEditEnt, catEditEnt\
            ,statusEditCombo, locationEditEnt, makeEditEnt, dBoughtEditEnt, notesEditBtn\
            , findBtn, updateBtn, delEntBtn, clearBtn)
for widget in newOrder:
    widget.lift()

# -----------------------------------Search Tab--------------------------------------
# Labels
assetNameSearch = Label(searchTab, text='Asset Name: ', font=('Courier', 10))
assetTagSearch = Label(searchTab, text='Asset Tag: ', font=('Courier', 10))
serialNumSearch = Label(searchTab, text='Serial Number: ', font=('Courier', 10))
modelSearch = Label(searchTab, text='Model: ', font=('Courier', 10))
catSearch = Label(searchTab, text='Category: ', font=('Courier', 10))
statusSearch = Label(searchTab, text='Status: ', font=('Courier', 10))
locationSearch = Label(searchTab, text='Location: ', font=('Courier', 10))
dBoughtSearch = Label(searchTab, text='Date Bought: ', font=('Courier', 10))
makeSearch = Label(searchTab, text = 'Make: ', font=('Courier', 10))
notesSearch = Label(searchTab, text = 'Keyword in Notes: ', font=('Courier', 10))

# Buttons
searchBtn = Button(searchTab, text = 'Search', command=search)
clearSrcBtn = Button(searchTab, text = 'Clear', command = clearSearch)
printSrcBtn = Button(searchTab, text = 'Print', command = printWindow)
dBoughtSearchEnt = Button(searchTab, text = 'Choose Date', command = lambda: chooseDate(dBoughtSearchEnt))

# Entries
assetNameSearchEnt = Entry(searchTab, width=10, font=('Courier', 10))
assetTagSearchEnt = Entry(searchTab, width=10, font=('Courier', 10))
serialNumSearchEnt = Entry(searchTab, width=10, font=('Courier', 10))
modelSearchEnt = Entry(searchTab, width=10, font=('Courier', 10))
locationSearchEnt = Entry(searchTab, width=10, font=('Courier', 10))
makeSearchEnt = Entry(searchTab, width = 10, font=('Courier', 10))
noteSearchEnt = Entry(searchTab, width = 10, font=('Courier', 10))

# Combobox
statusSearchCombo = Combobox(searchTab, width=10, font=('Courier', 10))
catSearchEnt = Combobox(searchTab, width=10, font=('Courier', 10))

# Text Box
testTextContainer = Frame(searchTab, borderwidth = 1, relief = 'sunken')
textFrame = Frame(testTextContainer)
textSearchZero = Text(textFrame, font=('Courier', 10), width = 21, height = 2, wrap = 'none', borderwidth = 0, state = 'disabled')
textSearchZero2 = Text(textFrame, font=('Courier', 10), width = 55, height = 2, wrap = 'none', borderwidth = 0, state = 'disabled')
textSearchOne = Text(textFrame, font=('Courier', 10), width = 21, height = 15, wrap = 'none', borderwidth = 0, state = 'disabled')
textSearchTwo = Text(textFrame, font=('Courier', 10), width = 55, height = 15, wrap = 'none', borderwidth = 0, state = 'disabled')
VSB = Scrollbar(testTextContainer, orient = VERTICAL, command = viewall)
HSB = Scrollbar(testTextContainer, orient = HORIZONTAL, command = viewallH)
textSearchOne.bind('<MouseWheel>', on_mousewheel)
textSearchTwo.bind('<MouseWheel>', on_mousewheel)
textSearchZero.bind('<MouseWheel>', removeScrollWheel)
textSearchZero2.bind('<MouseWheel>', removeScrollWheel)
textSearchTwo.configure(yscrollcommand = VSB.set, xscrollcommand = HSB.set)
textSearchOne.configure(yscrollcommand = VSB.set)
textSearchZero.grid(row = 0, column = 0, columnspan = 2, sticky = N+S+E+W)
textSearchZero2.grid(row = 0, column = 1, columnspan = 2, sticky = N+S+E+W)
textSearchOne.grid(row = 1, column = 0, sticky = N+S+E+W)
textSearchTwo.grid(row = 1, column = 1, columnspan = 5, sticky = N+S+E+W)
Grid.columnconfigure(textFrame, 0, weight = 0)
Grid.columnconfigure(textFrame, 1, weight = 1)
Grid.rowconfigure(textFrame, 0, weight = 0)
Grid.rowconfigure(textFrame, 1, weight = 1)
textFrame.grid(row = 0, column = 0, sticky = N+S+E+W)
VSB.grid(row = 0, column = 2, sticky = N+S+E+W)
HSB.grid(row = 1, column = 0, sticky = N+S+E+W)
Grid.rowconfigure(testTextContainer, 0, weight = 1)
Grid.columnconfigure(testTextContainer, 0, weight = 1)
Grid.columnconfigure(testTextContainer, 1, weight = 0)

# Grid Building
assetNameSearch.grid(row=0, column=0, padx=5, pady=5, sticky = N+S)
assetNameSearchEnt.grid(row=0, column=1, padx=5, pady=5, sticky = E+W)
assetTagSearch.grid(row=0, column=2, padx=5, pady=5, sticky = N+S)
assetTagSearchEnt.grid(row=0, column=3, padx=5, pady=5, sticky = E+W)
serialNumSearch.grid(row=0, column=4, padx=5, pady=5, sticky = N+S)
serialNumSearchEnt.grid(row=0, column=5, padx=5, pady=5, sticky = E+W)
makeSearch.grid(row=1, column=0, padx=5, pady=5, sticky = N+S)
makeSearchEnt.grid(row=1, column=1, padx=5, pady=5, sticky = E+W)
modelSearch.grid(row=1, column=2, padx=5, pady=5, sticky = N+S)
modelSearchEnt.grid(row=1, column=3, padx=5, pady=5, sticky = E+W)
catSearch.grid(row=1, column=4, padx=5, pady=5, sticky = N+S)
catSearchEnt.grid(row=1, column=5, padx=5, pady=5, sticky = E+W)
statusSearch.grid(row=2, column=0, padx=5, pady=5, sticky = N+S)
statusSearchCombo.grid(row=2, column=1, padx=5, pady=5, sticky = E+W)
locationSearch.grid(row=2, column=2, padx=5, pady=5, sticky = N+S)
locationSearchEnt.grid(row=2, column=3, padx=5, pady=5, sticky = E+W)
dBoughtSearch.grid(row=2, column=4, padx=5, pady=5, sticky = N+S)
dBoughtSearchEnt.grid(row=2, column=5, padx=5, pady=5, sticky = E+W)
notesSearch.grid(row = 3, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = N+S)
noteSearchEnt.grid(row = 3, column = 2, columnspan = 4, padx = 5, pady = 5, sticky = E+W)
searchBtn.grid(row=4, column=0, columnspan = 2, padx=5, pady=5, sticky = N+S+E+W)
clearSrcBtn.grid(row = 4, column = 2, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
printSrcBtn.grid(row = 4, column = 4, columnspan = 2, padx = 5, pady = 5, sticky = N+S+E+W)
testTextContainer.grid(row=5, column=0, columnspan=200, rowspan=10, padx=5, pady=5, sticky = N+S+E+W)
for x in range(5):
    Grid.rowconfigure(searchTab, x, weight = 2)
Grid.rowconfigure(searchTab, 5, weight = 100)
for y in range(6):
    Grid.columnconfigure(searchTab, y, weight = 1)
newOrder = (assetNameSearchEnt, assetTagSearchEnt, serialNumSearchEnt, modelSearchEnt\
                , catSearchEnt, statusSearchCombo, locationSearchEnt, makeSearchEnt, dBoughtSearchEnt\
                , searchBtn, clearSrcBtn, testTextContainer)
for widget in newOrder:
    widget.lift()

# -----------------------------------Insert Tab-----------------------------------
# Combobox
status = Combobox(insertionTab, width = 5, font=('Courier', 10))
cat = Combobox(insertionTab, width=5, font=('Courier', 10))

# Text Box
textContainer = Frame(insertionTab, borderwidth=1, relief='sunken')
text = Text(textContainer, font=('Courier', 10), width=30, height=30, wrap='none', borderwidth=0)
textVsb = Scrollbar(textContainer, orient="vertical", command=text.yview)
textHsb = Scrollbar(textContainer, orient="horizontal", command=text.xview)
text.configure(yscrollcommand=textVsb.set, xscrollcommand=textHsb.set, state = 'disabled')
text.grid(row=0, column=0, sticky=N+S+W+E)
textVsb.grid(row=0, column=1, sticky=N+S+W+E)
textHsb.grid(row=1, column=0, sticky=N+S+W+E)
for x in range(1):
    Grid.rowconfigure(textContainer, x, weight = 1)
Grid.columnconfigure(textContainer, 0, weight = 1)
Grid.columnconfigure(textContainer, 1, weight = 0)

# Labels
assetNameLabel = Label(insertionTab, text='Asset Name: ', font=('Courier', 12))
assetTagLabel = Label(insertionTab, text='Asset Tag: ', font=('Courier', 12))
serialNumLabel = Label(insertionTab, text='Serial Number: ', font=('Courier', 12))
modelLabel = Label(insertionTab, text='Model: ', font=('Courier', 12))
catLabel = Label(insertionTab, text='Category: ', font=('Courier', 12))
statusLabel = Label(insertionTab, text='Status: ', font=('Courier', 12))
locationLabel = Label(insertionTab, text='Location: ', font=('Courier', 12))
dBoughtLabel = Label(insertionTab, text='Date Bought: ', font=('Courier', 12))
makeLabel = Label(insertionTab, text = 'Make: ', font=('Courier', 12))
notesLabel = Label(insertionTab, text = 'Notes: ', font=('Courier', 12))

#Frames
btnFrame = Frame(insertionTab)

# Buttons
pushBtn = Button(btnFrame, text='Push Entry', command=pushEnt)
finisBtn = Button(btnFrame, text='Push to Database', command = DBExport)
delBtn = Button(btnFrame, text='Delete Last Entry', command=delPrevEnt)
saveBtn = Button(btnFrame, text = 'Save for Later', command = saveInsertForLater)
importBtn = Button(btnFrame, text = 'Import Saved Data', command = insertSavedData)
dBought = Button(insertionTab, text = 'Choose Date', command = lambda: chooseDate(dBought))
notesBtn = Button(insertionTab, text = 'Insert Notes', command = lambda: notesEditor(currentNotesInsert, 'insert', notesBtn))

# Entries
assetName = Entry(insertionTab, width=10, font=('Courier', 10))
assetTag = Entry(insertionTab, width=10, font=('Courier', 10))
serialNum = Entry(insertionTab, width=10, font=('Courier', 10))
model = Entry(insertionTab, width=10, font=('Courier', 10))
location = Entry(insertionTab, width=10, font=('Courier', 10))
make = Entry(insertionTab, width=10, font=('Courier', 10))

# Grid Building
textContainer.grid(row=0, column=3, rowspan = 100, padx = 5, pady = 5, sticky = N+S+E+W)
assetNameLabel.grid(row=0, column=0, padx=5, pady=5, sticky = N+S+W+E)
assetName.grid(row=0, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
assetTagLabel.grid(row=1, column=0, padx=5, pady=5, sticky = N+S+W+E)
assetTag.grid(row=1, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
serialNumLabel.grid(row=2, column=0, padx=5, pady=5, sticky = N+S+W+E)
serialNum.grid(row=2, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
makeLabel.grid(row=3, column=0, padx=5, pady=5, sticky = N+S+W+E)
make.grid(row=3, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
modelLabel.grid(row=4, column=0, padx=5, pady=5, sticky = N+S+W+E)
model.grid(row=4, column=1, padx=5, columnspan = 2, pady=5, sticky = E+W)
catLabel.grid(row=5, column=0, padx=5, pady=5, sticky = N+S+W+E)
cat.grid(row=5, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
statusLabel.grid(row=6, column=0, padx=5, pady=5, sticky = N+S+W+E)
status.grid(row=6, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
locationLabel.grid(row=7, column=0, padx=5, pady=5, sticky = N+S+W+E)
location.grid(row=7, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
dBoughtLabel.grid(row=8, column=0, padx=5, pady=5, sticky = N+S+W+E)
dBought.grid(row=8, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
notesLabel.grid(row=9, column=0, padx=5, pady=5, sticky = N+S+W+E)
notesBtn.grid(row=9, column=1, columnspan = 2, padx=5, pady=5, sticky = E+W)
btnFrame.grid(row = 10, column = 0, columnspan = 3, padx = 5, pady = 5, sticky = N+S+E+W)
pushBtn.grid(row=0, column=0, padx=5, pady=5, sticky = N+S+E+W)
delBtn.grid(row=0, column=1, padx=5, pady=5, sticky = N+S+E+W)
saveBtn.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = N+S+E+W)
importBtn.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = N+S+E+W)
finisBtn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky = N+S+E+W)

for y in range(0, 2):
    Grid.columnconfigure(btnFrame, y, weight = 1)
for x in range(0, 13):
    Grid.rowconfigure(insertionTab, x, weight = 1)
Grid.columnconfigure(insertionTab, 0, weight = 1)
Grid.columnconfigure(insertionTab, 1, weight = 2)
Grid.columnconfigure(insertionTab, 2, weight = 1)
Grid.columnconfigure(insertionTab, 3, weight = 50)
newOrder = (assetName, assetTag, serialNum, make, model, cat, status, location, dBought, notesBtn, pushBtn, delBtn\
            , finisBtn)
for widget in newOrder:
    widget.lift()

#----------------------------------------------------Execute--------------------------------------------
icon = \
"""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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEcAAAD+AAAA/wAAAP8AAAD/AAAAWgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWQAAAP8AAAD/AAAA/wAAAP4AAABHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAA4wAAAP8AAAD/AAAA/wAAAP8AAACVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACTAAAA/wAAAP8AAAD/AAAA/wAAAOMAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJ8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMAAAA/wAAAP8AAAD/AAAA/wAAAP8AAADQAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAANAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEgAAAOYAAAD/AAAA/wAAAP8AAAD/AAAA+QAAAC8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALwAAAPkAAAD/AAAA/wAAAP8AAAD/AAAA5gAAABIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAClAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAB9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAApQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAywAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAywAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAUgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABUAAADpAAAA/wAAAP8AAAD/AAAA/wAAAPgAAAArAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArAAAA+AAAAP8AAAD/AAAA/wAAAP8AAADpAAAAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAdwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB3AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACrAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFgAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMcAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAADHAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA7AAAAP8AAAD/AAAA/wAAAP8AAAD2AAAAJwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAD2AAAA/wAAAP8AAAD/AAAA/wAAAOwAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAHEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABdAAAA/wAAAP8AAAD/AAAA/wAAAP8AAADCAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAMIAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAF0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAO4AAAD/AAAA/wAAAP8AAAD/AAAA9AAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAPQAAAD/AAAA/wAAAP8AAAD/AAAA7gAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACkAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAApAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQQAAAP4AAAD/AAAA/wAAAP8AAAD/AAAAvQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAvQAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAADUAAAA/wAAAP8AAAD/AAAA/wAAAPYAAAAhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhAAAA9gAAAP8AAAD/AAAA/wAAAP8AAADUAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAewAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAIgAAADEAAAAxAAAAFgAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAWAAAAMQAAADEAAAAhAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAADTAAAA/wAAAP8AAAD/AAAA/wAAANgAAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAEIAAACRAAAA0AAAAPoAAAD/AAAA/wAAAP8AAAD/AAAA5QAAAJQAAAAmAAAAAAAAAAAAAAAAAAAAAAAAACYAAACUAAAA5QAAAP8AAAD/AAAA/wAAAP8AAAD6AAAA0AAAAJEAAABCAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcAAADYAAAA/wAAAP8AAAD/AAAA/wAAANMAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAVgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAG0AAADgAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPoAAACJAAAAAwAAAAMAAACJAAAA+gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADgAAAAbQAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAFEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4AAAA/wAAAP8AAAD/AAAA/wAAANUAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEoAAADdAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAC0AAAAtAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA3QAAAEoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAANUAAAD/AAAA/wAAAP8AAAD/AAAAuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAP0AAAD/AAAA/wAAAP8AAAD/AAAAWwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAACPAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/gAAAI8AAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWwAAAP8AAAD/AAAA/wAAAP8AAAD9AAAAHgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB+AAAA/wAAAP8AAAD/AAAA/wAAAO0AAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAswAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADvAAAA5gAAAP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/QAAAOYAAADvAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAALMAAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAA7AAAAP8AAAD/AAAA/wAAAP8AAAB+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM4AAAD/AAAA/wAAAP8AAAD/AAAAkgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAL0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAAHwAAAAxAAAACQAAAAAAAAAAAAAAGQAAAJMAAAD+AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/gAAAJMAAAAZAAAAAAAAAAAAAAAJAAAAMQAAAHwAAADOAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAL0AAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQAAAA/wAAAP8AAAD/AAAA/wAAAM4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAC9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA1QAAAE8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAB7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABPAAAA1QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAL0AAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIAAAD/AAAA/wAAAP8AAAD/AAAA/gAAABkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGEAAAD/AAAA/wAAAP8AAAD/AAAA5gAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAvQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJwAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAOAAAAD/AAAA/wAAAP8AAAD/AAAA4AAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAnAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAL0AAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAOUAAAD/AAAA/wAAAP8AAAD/AAAAYQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAAP8AAAD/AAAA/wAAAP8AAACeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFwAAAMQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAAByAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnQAAAP8AAAD/AAAA/wAAAP8AAACdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcgAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMQAAAAXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnQAAAP8AAAD/AAAA/wAAAP8AAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAFsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADcAAADhAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAawAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACNAAAA/wAAAP8AAAD/AAAA/wAAAI0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAawAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOEAAAA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABbAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAPoAAAD/AAAA/wAAAP8AAAD/AAAAKgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACkAAACpAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/gAAAGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAABdAAAAvwAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA/AAAAL4AAABcAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbAAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAACpAAAAKQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACkAAAD/AAAA/wAAAP8AAAD/AAAA+gAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxAAAA/wAAAP8AAAD/AAAA/wAAAPUAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAACQAAABFAAAAXgAAAIgAAADUAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAABsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAA0gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADSAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbAAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA1AAAAIgAAABeAAAARQAAACQAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAPQAAAD/AAAA/wAAAP8AAAD/AAAAMQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAE0AAAD/AAAA/wAAAP8AAAD/AAAA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABcAAADNAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD5AAAAWwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVAAAAPYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD2AAAAVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWwAAAPkAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAM0AAAAXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzgAAAP8AAAD/AAAA/wAAAP8AAABNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZgAAAP8AAAD/AAAA/wAAAP8AAAC2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAANcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEgAAAD6AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD6AAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC1AAAA/wAAAP8AAAD/AAAA/wAAAGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/AAAA/wAAAP8AAAD/AAAA/wAAAJ0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA+AAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXAAAA6gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAO4AAADEAAAAxAAAAO4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADqAAAAFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAD4AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAuwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJwAAAD/AAAA/wAAAP8AAAD/AAAAfwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIoAAAD/AAAA/wAAAP8AAAD/AAAAiwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA5wAAAP0AAAD/AAAA/wAAAP8AAAD/AAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAN4AAABRAAAABAAAAAAAAAAAAAAABAAAAFEAAADeAAAA/wAAAP8AAAD/AAAA/wAAAP8AAACdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAP8AAAD/AAAA/wAAAP8AAAD9AAAA5wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiwAAAP8AAAD/AAAA/wAAAP8AAACKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiwAAAP8AAAD/AAAA/wAAAP8AAACKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAIAAAADUAAAA2wAAAMsAAACpAAAAeQAAADoAAAACAAAA1AAAAP8AAAD/AAAA/wAAAP8AAABiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA+AAAAP8AAAD/AAAA/wAAAP8AAADOAAAAEQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAADOAAAA/wAAAP8AAAD/AAAA/wAAAPgAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABiAAAA/wAAAP8AAAD/AAAA/wAAANUAAAACAAAAOwAAAHkAAACpAAAAywAAANsAAADUAAAAgAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACKAAAA/wAAAP8AAAD/AAAA/wAAAIsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAAAA/wAAAP8AAAD/AAAA/wAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAA/wAAAP8AAAD/AAAA/wAAAKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGYAAAD/AAAA/wAAAP8AAAD/AAAA9gAAACIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACIAAAD2AAAA/wAAAP8AAAD/AAAA/wAAAGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKUAAAD/AAAA/wAAAP8AAAD/AAAAnAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIgAAAD/AAAA/wAAAP8AAAD/AAAAjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkAAAD/AAAA/wAAAP8AAAD/AAAAjwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF0AAAD/AAAA/wAAAP8AAAD/AAAA8gAAAAsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApgAAAP8AAAD/AAAA/wAAAP8AAACcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJwAAAD/AAAA/wAAAP8AAAD/AAAApgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAA8gAAAP8AAAD/AAAA/wAAAP8AAABeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjwAAAP8AAAD/AAAA/wAAAP8AAACJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdAAAAP8AAAD/AAAA/wAAAP8AAACmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAPkAAAD/AAAA/wAAAP8AAAD/AAAAXwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADFAAAA/wAAAP8AAAD/AAAA/wAAAGMAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAABAAAAAQAAAAYwAAAP8AAAD/AAAA/wAAAP8AAADFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF8AAAD/AAAA/wAAAP8AAAD/AAAA+QAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACmAAAA/wAAAP8AAAD/AAAA/wAAAHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABeAAAA/wAAAP8AAAD/AAAA/wAAAL0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtAAAAP8AAAD/AAAA/wAAAP8AAADQAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAANUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAA0AAAAP8AAAD/AAAA/wAAAP8AAAC0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL0AAAD/AAAA/wAAAP8AAAD/AAAAXgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEcAAAD/AAAA/wAAAP8AAAD/AAAA2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABNAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAtwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2AAAAP8AAAD/AAAA/wAAAP8AAABHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKQAAAP8AAAD/AAAA/wAAAP8AAAD4AAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAADZAAAA/wAAAP8AAAD/AAAA/wAAANsAAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABbAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAA2wAAAP8AAAD/AAAA/wAAAP8AAADZAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAD4AAAA/wAAAP8AAAD/AAAA/wAAACkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAA/QAAAP8AAAD/AAAA/wAAAP8AAAAeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGIAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAACpAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAqQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAP8AAAD/AAAA/wAAAP8AAAD9AAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADiAAAA/wAAAP8AAAD/AAAA/wAAAEEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAM8AAAD/AAAA/wAAAP8AAAD/AAAA/AAAAEkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAABwAAAA2QAAAP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD9AAAA2QAAAHAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABJAAAA/AAAAP8AAAD/AAAA/wAAAP8AAADPAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBAAAA/wAAAP8AAAD/AAAA/wAAAOIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAD/AAAA/wAAAP8AAAD/AAAAYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPgAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA8AAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAgAAAAIAAAACAAAAAgAAAAIAAAACAAAAAgAAAAIAAAACAAAAAgAAAAIAAAACAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAPAAAAD/AAAA/wAAAP8AAAD/AAAA/gAAAD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGMAAAD/AAAA/wAAAP8AAAD/AAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnQAAAP8AAAD/AAAA/wAAAP8AAACGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA4wAAACYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYAAADjAAAA/wAAAP8AAAD/AAAA/wAAAP8AAACOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhgAAAP8AAAD/AAAA/wAAAP8AAACdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6AAAA/wAAAP8AAAD/AAAA/wAAAKkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAA0AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA5gAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAA5gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA0AAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACpAAAA/wAAAP8AAAD/AAAA/wAAAHoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFgAAAD/AAAA/wAAAP8AAAD/AAAAywAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfAAAA5wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA9QAAAF4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXgAAAPUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOcAAAAfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMsAAAD/AAAA/wAAAP8AAAD/AAAAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANQAAAP8AAAD/AAAA/wAAAP8AAADuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzAAAA8wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJcAAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAJcAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADzAAAAMwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA7gAAAP8AAAD/AAAA/wAAAP8AAAA1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAAA7gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAADHAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA7gAAADgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAAD/AAAA/wAAAP8AAAD/AAAA/wAAABIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADvAAAA/wAAAP8AAAD/AAAA/wAAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuAAAA4wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAM0AAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAAAAzQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOMAAAAuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAAAAP8AAAD/AAAA/wAAAP8AAADvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAAD/AAAA/wAAAP8AAAD/AAAAVwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVAAAAuwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAL4AAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAL4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAC7AAAAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABXAAAA/wAAAP8AAAD/AAAA/wAAAMwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqQAAAP8AAAD/AAAA/wAAAP8AAAB6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAyAAAATAAAAFUAAABHAAAAIAAAAAEAAAAAAAAAAAAAAAAAAAADAAAAhAAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAIcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACHAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAhAAAAAMAAAAAAAAAAAAAAAAAAAABAAAAIAAAAEcAAABVAAAATAAAADIAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHoAAAD/AAAA/wAAAP8AAAD/AAAAqQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACHAAAA/wAAAP8AAAD/AAAA/wAAAJwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEkAAACtAAAA9gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA4wAAAI8AAAAjAAAAAAAAAAAAAAAAAAAAVgAAAPsAAAD/AAAA/wAAAP8AAAD/AAAA/AAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA+wAAAFYAAAAAAAAAAAAAAAAAAAAjAAAAjwAAAOMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPYAAACtAAAASQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAAAAP8AAAD/AAAA/wAAAP8AAACHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGQAAAD/AAAA/wAAAP8AAAD/AAAAvwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkAAADBAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPwAAACQAAAADAAAAAAAAAAAAAAAXAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAwgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADCAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABcAAAAAAAAAAAAAAAMAAAAkAAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAwQAAABkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC/AAAA/wAAAP8AAAD/AAAA/wAAAGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQQAAAP8AAAD/AAAA/wAAAP8AAADiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADSAAAAHwAAAAAAAAAAAAAAlAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAlAAAAAAAAAAAAAAAHwAAANIAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAuwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOIAAAD/AAAA/wAAAP8AAAD/AAAAQQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfAAAA/wAAAP8AAAD/AAAA/wAAAP0AAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD3AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADdAAAAGgAAAAAAAAANAAAA5QAAAP8AAAD/AAAA/wAAAP8AAACpAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACpAAAA/wAAAP8AAAD/AAAA/wAAAOUAAAANAAAAAAAAABoAAADdAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAA/QAAAP8AAAD/AAAA/wAAAP8AAAAfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAD5AAAA/wAAAP8AAAD/AAAA/wAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMkAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAN0AAADDAAAA3QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADCAAAAAwAAAAAAAABwAAAA/wAAAP8AAAD/AAAA/wAAAPQAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQAAAPQAAAD/AAAA/wAAAP8AAAD/AAAAcAAAAAAAAAADAAAAwgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADdAAAAwwAAAN0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAD/AAAA/wAAAP8AAAD/AAAA+QAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOYAAAD/AAAA/wAAAP8AAAD/AAAASwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAzgAAABcAAAAAAAAAIwAAAJUAAAD9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABcAAAAAAAAAA4AAAD3AAAA/wAAAP8AAAD/AAAA/wAAAEkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABJAAAA/wAAAP8AAAD/AAAA/wAAAPcAAAAOAAAAAAAAAFwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP0AAACVAAAAIwAAAAAAAAAXAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAARQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASwAAAP8AAAD/AAAA/wAAAP8AAADZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA8AAAAKEAAACMAAAAxwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAI8AAAAAAAAAAAAAALUAAAD/AAAA/wAAAP8AAAD/AAAAfQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH0AAAD/AAAA/wAAAP8AAAD/AAAAtQAAAAAAAAAAAAAAjwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMcAAACMAAAAoQAAAPAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAKQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABtAAAA/wAAAP8AAAD/AAAA/wAAAPIAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXAAAA6gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAVgAAAAAAAAAAAAAAfgAAAP8AAAD/AAAA/wAAAP8AAACqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqgAAAP8AAAD/AAAA/wAAAP8AAAB+AAAAAAAAAAAAAABWAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADqAAAAFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAswAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFAAAA/AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/QAAAIYAAAABAAAAAAAAAAAAAABZAAAA/wAAAP8AAAD/AAAA/wAAAL4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC+AAAA/wAAAP8AAAD/AAAA/wAAAFkAAAAAAAAAAAAAAAEAAACGAAAA/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/AAAAEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAswAAAP8AAAD/AAAA/wAAAP8AAAD/AAAArAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADdAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABOAAAA9AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAM8AAAA2AAAAAAAAAAAAAAAAAAAAAAAAAEoAAAD/AAAA/wAAAP8AAAD/AAAAzQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM0AAAD/AAAA/wAAAP8AAAD/AAAASgAAAAAAAAAAAAAAAAAAAAAAAAA2AAAAzwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPQAAABOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAADdAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD3AAAADgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACdAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiAAAAqwAAAPsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOEAAABoAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAaAAAAOEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPsAAACrAAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAnQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAADjAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFQAAAFsAAACAAAAAiQAAAHUAAAA7AAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAADsAAAB1AAAAiQAAAIAAAABbAAAAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAALYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA0QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAARgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABtAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA+gAAAA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAByAAAA/wAAAP8AAAD/AAAA/wAAAPgAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP0AAABXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVwAAAP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAAD/AAAA/wAAAP8AAAD/AAAATQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALcAAAD/AAAA/wAAAP8AAAD/AAAAhwAAAKAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPkAAABEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQAAAD5AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACgAAAAsAAAAP8AAAD/AAAA/wAAAP8AAACSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAA9AAAAP8AAAD/AAAA/wAAAP8AAABDAAAABAAAALQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPIAAAAzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA0QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAARgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzAAAA8gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAtQAAAAUAAABqAAAA/wAAAP8AAAD/AAAA/wAAANcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAD/AAAA/wAAAP8AAAD/AAAA9gAAAAgAAAAAAAAACgAAAMYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOkAAAAkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAOkAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMYAAAAKAAAAAAAAACQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAB0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhQAAAP8AAAD/AAAA/wAAAP8AAAC6AAAAAAAAAAAAAAAAAAAAEwAAANYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAN0AAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAADdAAAA/wAAAP8AAAD/AAAA/wAAAP8AAADWAAAAEwAAAAAAAAAAAAAAAAAAAN4AAAD/AAAA/wAAAP8AAAD/AAAAYgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC/AAAA/wAAAP8AAAD/AAAA/wAAAHYAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAOMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAM4AAAAOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA0QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAARgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAAAAzgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA4wAAAB4AAAAAAAAAAAAAAAAAAAAAAAAAmQAAAP8AAAD/AAAA/wAAAP8AAACjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAPAAAAD/AAAA/wAAAP8AAAD/AAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKwAAAO0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAL4AAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAL4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAO0AAAArAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABaAAAA/wAAAP8AAAD/AAAA/wAAANcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkAAAA/wAAAP8AAAD/AAAA/wAAAPwAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOgAAAPUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAKsAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAACrAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD2AAAAOwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYAAAD/AAAA/wAAAP8AAAD/AAAA/QAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFYAAAD/AAAA/wAAAP8AAAD/AAAA0wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATQAAAPsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA0QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAARgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA+wAAAE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAO8AAAD/AAAA/wAAAP8AAAD/AAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiAAAAP8AAAD/AAAA/wAAAP8AAACfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYQAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAH0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP4AAABiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuwAAAP8AAAD/AAAA/wAAAP8AAABvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC6AAAA/wAAAP8AAAD/AAAA/wAAAGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAeQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAANEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABlAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAeQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACHAAAA/wAAAP8AAAD/AAAA/wAAAKEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOcAAAD/AAAA/wAAAP8AAAD/AAAAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/AAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA0QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAARgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFYAAAD/AAAA/wAAAP8AAAD/AAAA0wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAAbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAApgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA9wAAAD0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARgAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD0AAAD3AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACmAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAP8AAAD/AAAA/wAAAP8AAAD3AAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACkAAAD/AAAA/wAAAP8AAAD/AAAA9AAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAugAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA7wAAAC0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+AAAA/wAAAP8AAAD/AAAA/wAAAMkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADJAAAA/wAAAP8AAAD/AAAA/wAAAD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtAAAA7wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAugAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAAZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASQAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAAAA2AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA5QAAAB8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0AAADsAAAA/wAAAP8AAAD/AAAAhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIYAAAD/AAAA/wAAAP8AAADsAAAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHwAAAOUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAANcAAAANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADlAAAA/wAAAP8AAAD/AAAA/wAAADkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABqAAAA/wAAAP8AAAD/AAAA/wAAAK0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA2AAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADwAAADOAAAA6wAAAJoAAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQAAAJoAAADrAAAAzgAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAADYAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL8AAAD/AAAA/wAAAP8AAAD/AAAAWQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkAAAD/AAAA/wAAAP8AAAD/AAAAjQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAyQAAAAsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAAyQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAAAAP8AAAD/AAAA/wAAAP8AAAB5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqQAAAP8AAAD/AAAA/wAAAP8AAAB3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAtwAAAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAALcAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAdgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEAAAA/wAAAP8AAAD/AAAA/wAAAJkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC7AAAA/wAAAP8AAAD/AAAA/wAAAGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAowAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAACjAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG8AAAD/AAAA/wAAAP8AAAD/AAAAsgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMkAAAD/AAAA/wAAAP8AAAD/AAAATQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAA6QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWgAAAP8AAAD/AAAA/wAAAP8AAADBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1wAAAP8AAAD/AAAA/wAAAP8AAAA5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACuAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAA/wAAAP8AAAD/AAAA/wAAANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADmAAAA/wAAAP8AAAD/AAAA/wAAACYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAXgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABeAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC8AAAD/AAAA/wAAAP8AAAD/AAAA3gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPQAAAD/AAAA/wAAAP8AAAD/AAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD6AAAASQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASQAAAPoAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAP8AAAD/AAAA/wAAAP8AAADtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA6AAAA/wAAAP8AAAD/AAAA/wAAAPUAAACtAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD1AAAATgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAE0AAAD1AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACtAAAA9QAAAP8AAAD/AAAA/wAAAP8AAAAtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdAAAA/wAAAP8AAAD/AAAA/wAAAPsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAD/AAAA/wAAAP8AAAD/AAAA/wAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAABMAAADAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD8AAAAmwAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAAACbAAAA/AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAwAAAABMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAABEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABcAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPgAAAD/AAAA/wAAAP8AAAD/AAAAJAAAABAAAADRAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAANUAAACyAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAAKIAAACiAAAAogAAALIAAADVAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAANEAAAAQAAAAJAAAAP8AAAD/AAAA/wAAAP8AAAD4AAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA6gAAAP8AAAD/AAAA/wAAAP8AAAA3AAAAAAAAABoAAADaAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADaAAAAGgAAAAAAAAA4AAAA/wAAAP8AAAD/AAAA/wAAAOQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD+AAAA/wAAAP8AAAD/AAAA/wAAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeAAAA/wAAAP8AAAD/AAAA/wAAAEIAAAAAAAAAAAAAABgAAADiAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA0QAAABcAAAAAAAAAAAAAAEMAAAD/AAAA/wAAAP8AAAD/AAAA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPsAAAD/AAAA/wAAAP8AAAD/AAAAGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANEAAAD/AAAA/wAAAP8AAAD/AAAATgAAAAAAAAAAAAAAKAAAAPoAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADPAAAAAwAAAAAAAAAAAAAATQAAAP8AAAD/AAAA/wAAAP8AAADVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9wAAAP8AAAD/AAAA/wAAAP8AAAAiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxQAAAP8AAAD/AAAA/wAAAP8AAABRAAAAAAAAAAAAAAC4AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABoAAAAAAAAAAAAAABVAAAA/wAAAP8AAAD/AAAA/wAAAM4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcAAAA/wAAAP8AAAD/AAAA/wAAAPsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADyAAAA/wAAAP8AAAD/AAAA/wAAACwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADGAAAA/wAAAP8AAAD/AAAA/wAAAE0AAAAAAAAATwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAmAAAACgAAABWAAAAawAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAAB2AAAAdgAAAHYAAABrAAAAVQAAAC0AAADeAAAA/wAAAP8AAAD/AAAA/wAAAOwAAAASAAAAAAAAAFQAAAD/AAAA/wAAAP8AAAD/AAAAxwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYAAAD/AAAA/wAAAP8AAAD/AAAA9wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAAAAD/AAAA/wAAAP8AAAD/AAAANQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMsAAAD/AAAA/wAAAP8AAAD/AAAASAAAAAgAAADdAAAA/wAAAP8AAAD/AAAA/wAAAO0AAAATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJUAAAAAAAAAUwAAAP8AAAD/AAAA/wAAAP8AAADEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALwAAAP8AAAD/AAAA/wAAAP8AAADsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAygAAAP8AAAD/AAAA/wAAAP8AAABGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0QAAAP8AAAD/AAAA/wAAAP8AAABEAAAAewAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAawAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALoAAAD/AAAA/wAAAP8AAAD/AAAA/AAAAC8AAABQAAAA/wAAAP8AAAD/AAAA/wAAANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA7AAAA/wAAAP8AAAD/AAAA/wAAANcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC2AAAA/wAAAP8AAAD/AAAA/wAAAF8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADWAAAA/wAAAP8AAAD/AAAA/wAAAFwAAAD0AAAA/wAAAP8AAAD/AAAA/wAAANEAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKQAAAPoAAAD/AAAA/wAAAP8AAAD/AAAAwQAAAEUAAAD/AAAA/wAAAP8AAAD/AAAA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFIAAAD/AAAA/wAAAP8AAAD/AAAAwQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKEAAAD/AAAA/wAAAP8AAAD/AAAAeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOMAAAD/AAAA/wAAAP8AAAD/AAAA3AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAkQAAAP8AAAD/AAAA/wAAAP8AAADoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAawAAAP8AAAD/AAAA/wAAAP8AAACsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiwAAAP8AAAD/AAAA/wAAAP8AAACRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAKcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAAAA6AAAAP8AAAD/AAAA/wAAAP8AAAD5AAAA/wAAAP8AAAD/AAAA/wAAAPQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDAAAA/wAAAP8AAAD/AAAA/wAAAJcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB3AAAA/wAAAP8AAAD/AAAA/wAAAKoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD0AAAAHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/gAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJwAAAD/AAAA/wAAAP8AAAD/AAAAggAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFkAAAD/AAAA/wAAAP8AAAD/AAAAxwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAHsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAADJAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtQAAAP8AAAD/AAAA/wAAAP8AAABrAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMQAAAP8AAAD/AAAA/wAAAP8AAADvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADdAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYAAAD9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADZAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAA/gAAAP8AAAD/AAAA/wAAAP8AAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFgAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAE8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAFYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAPsAAAD/AAAA/wAAAP8AAAD/AAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADiAAAA/wAAAP8AAAD/AAAA/wAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAC4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFwAAAPAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArAAAA/wAAAP8AAAD/AAAA/wAAAPUAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALoAAAD/AAAA/wAAAP8AAAD/AAAAaQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACZAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA+gAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFMAAAD/AAAA/wAAAP8AAAD/AAAAzwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkwAAAP8AAAD/AAAA/wAAAP8AAACSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAA1gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAMEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAewAAAP8AAAD/AAAA/wAAAP8AAACoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABqAAAA/wAAAP8AAAD/AAAA/wAAAMEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA7wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA5wAAAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACnAAAA/wAAAP8AAAD/AAAA/wAAAIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsAAAD/AAAA/wAAAP8AAAD/AAAA8QAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACvAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANgAAAD/AAAA/wAAAP8AAAD/AAAAVQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQAAAP0AAAD/AAAA/wAAAP8AAAD/AAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASQAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAxwAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACIAAAD3AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAA/QAAAP8AAAD/AAAA/wAAAP8AAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2QAAAP8AAAD/AAAA/wAAAP8AAABTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0AAAA/wAAAP8AAAD/AAAA/wAAAP0AAAA1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAH0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADkAAAD/AAAA/wAAAP8AAAD/AAAA8gAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACpAAAA/wAAAP8AAAD/AAAA/wAAAIQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAnAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAOIAAAD/AAAA/wAAAP8AAAD/AAAA6QAAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAagAAAP8AAAD/AAAA/wAAAP8AAADDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHkAAAD/AAAA/wAAAP8AAAD/AAAAtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAADZAAAA/wAAAP8AAAD/AAAA/wAAAO8AAAAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAjwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACaAAAA/wAAAP8AAAD/AAAA/wAAAJMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASQAAAP8AAAD/AAAA/wAAAP8AAADkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAP8AAAD/AAAA/wAAAP8AAAD6AAAAKgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMoAAAD/AAAA/wAAAP8AAAD/AAAAYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkAAADyAAAA/wAAAP8AAAD/AAAA/wAAANQAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuAAAA/AAAAP8AAAD/AAAA/wAAAP8AAAC7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAA9wAAAP8AAAD/AAAA/wAAAP8AAAAyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADnAAAA/wAAAP8AAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAogAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAQwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACUAAAA/wAAAP8AAAD/AAAA/wAAAP8AAABRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAD/AAAA/wAAAP8AAAD/AAAA+gAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALcAAAD/AAAA/wAAAP8AAAD/AAAAfgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADoAAAD+AAAA/wAAAP8AAAD/AAAA/wAAAK0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAADrAAAA/wAAAP8AAAD/AAAA/wAAAN4AAAAJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXQAAAP8AAAD/AAAA/wAAAP8AAADRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfgAAAP8AAAD/AAAA/wAAAP8AAADZAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAzAAAAP8AAAD/AAAA/wAAAP8AAAD2AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGcAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAH0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACjAAAA/wAAAP8AAAD/AAAA/wAAAJ8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIEAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAM4AAAD/AAAA/wAAAP8AAAD/AAAA9QAAACUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJgAAAPgAAAD/AAAA/wAAAP8AAAD/AAAAXgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADNAAAA/wAAAP8AAAD/AAAA/wAAAP8AAACjAAAAFgAAAAAAAAAAAAAAAAAAABAAAACQAAAA/wAAAP8AAAD/AAAA/wAAAP8AAADgAAAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA1AAAABoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAAADYAAAA/wAAAP8AAAD/AAAA/wAAAPYAAAATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEYAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD7AAAAxAAAAKsAAADCAAAA9wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAE8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA7AAAAH0AAAA5AAAAIgAAADoAAACIAAAA9QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAlQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJcAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWAAAA6QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOgAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAK0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAsgAAAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABCAAAA9wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD3AAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAIEAAAD5AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/AAAAIcAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAAA7wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA7QAAAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACkAAACdAAAA9QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA9gAAAKYAAAAsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiAAAAsgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/gAAAK0AAAAdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAAPAAAAGAAAABxAAAAZQAAAEAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAI0AAADKAAAA7wAAAPsAAADqAAAAxQAAAIYAAAApAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/////g/////////wf/////////wP////////8D/////////4D/////////Af////////+A/////////wH/////////AP////////8A/////////gH/////////gH////////4D/////////8B////////8A//////////AP///////+Af/////////4B////////gP//////////Af///////wD//////////wD///////4B//////////+Af//////8A///////////wD///////AP//////////8A///////gH///////////gH//////4D///////////8B//////8A////////////AP/////+Af///////////4B//////gP////A/wP////Af/////wD///8ADwAP///wD/////8B///8AAAAA///+A//////Af//+AAAAAH///gP/////gP//+AAAAAAf//8B/////4D///AAAAAAD///Af////+B///gAMADAAf//4H/////Af//wAfwD+AD//+A/////wH//4Af8A/4Af//gP////8D//8AP/gf/AD//8D/////A//+AP/4H/8Af//A/////gP/+AH/wAP/gB//wH////4D/gAD/4AB/8AAf8B////+B/wAB/8AAP/gAD/gf////gf8AA/+AAB/8AA/4H////4H/AAH/AAAP+AAP+B////+B/wAB/wBgD/gAD/gf////gf8AAf4B+Af4AA/4H////4H//4H+A/wH+B//+B////+B//+A/gf+B/Af//gf////gf//gP4AAAfwH//4H////4H//8B+AAAH4D//+B////+B///AfgAAB+A///gf////gP//wD4AAAfAP//wH////4D//+A+AAAHwH//8B/////A///gHwAAD4B///A/////wP//8A/gAH8A///wP////8D///gH///+Af//8D/////A///4A////AH///A/////wP///AH///gD///wP////8D///4Af//gB///8D/////Af///AD//wA///+A/////4H///4Af/4Af///gf////+B////AD/8AP///4H/////gf/+A4A//AHAf/+B/////4H/8ADgH/gHAA//gf////+B/+AAMB/4DAAH/4H/////gf/gABgP8BgAB/+B/////4D/4AAID/AQAAf/Af////+A/+AABAfgIAAH/wH/////wP/gEAQH4CAIB/8D/////4D/8AAGB+BgAA//Af////+A//AABgfgYAAP/wH/////AP/4AAYH4GAAH/8B/////wB//AAeB+B4AD/+AP////8AP/4APgfgfAB//AD////+AD//gP4H4H8B//wA/////gAf///+B+B////4AH////4AD////gfgf///8AB////+AAf///4H4H///+AAf////AAD///+B+B////AAH////wEAf///gfgf///gCA////8DgD///4H4H///wBwP////A8Af//+B+B///4A8D////gPgD///gfgf//8AfA////4D8Af//4H4H//+APwH///+B/gD//+B+B///AH8B////gf8A///gfgf//wD/gf///4H/gH//4H4H//4B/4H///+B/8A//+B+B//8A/+B////Af/AH//gfgf/+AP/gP///wH/4A//4H4H//AH/4D///8D//AH/+B+B//gD//A////A//4A//wfg//wB//wP///wP//AH//////4A//8D///8D//wA//////8AP//A////A//8AH/////+AD//wP///wP//AB//////gA//8D///8D//4AP/////wAf//A////A//+AB/////4AH//wP///wP//gAP////8AB//8D///4D//4AB////+AAf//Af//+A//+AAH///+AAH//wH///gP//gAAAAAAAAB//8B///4D//8CAAAAAABA///Af//+A///AwAAAAAAwP//wH///wP//wMAAAAAAMD//8D///8D//8DAAAAAADA///A////A///AgAAAAAAQP//wP///wP//wAD////wED//8D///8D//8AB////8AA///A////A///AAf////gAP//wP///wP//wAP////8AD//8D///8D//8AH/////AA///A////A//+AB/////4AH//wP///wP//gA/////+AB//8D///8B//4AP/////wAf//A////Af/+AH/////+AH//gP///4H//gD//////gB//4D///+B//4A//////8Af/+B////gf/+Af//////AH//gf///4H//AH//////4B//4H///+A//wD///////AP/+B////gP/8A///////wD//Af///8D//Af//////+A//wH////A//gP///////gH/8D////wP/wD///////8B//A////8D/8B////////AP/wP////Af+Af///////4B/4D////4H/gP////////Af+A////+B/wH////////wD/gf////gP4B////////+A/4H////4D+A/////////gH8B////+AOAP////////8A+Af////wAAH/////////gAAP////+AAD/////////4AAD/////gAA//////////AAB/////8AAf/////////4AA//////wAf//////////AAf//////Af//////////8Af//8oAAAAQAAAAIAAAAABACAAAAAAAABAAACoDwAAqA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAawAAAPQAAAB2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHYAAADyAAAAaQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAAPgAAAD/AAAAvgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC9AAAA/wAAAPgAAAAsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAMwAAAD/AAAA/gAAAEEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQQAAAP4AAAD/AAAAzAAAAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH4AAAD/AAAA/wAAAJMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACTAAAA/wAAAP8AAAB+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAD5AAAA/wAAANsAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAANsAAAD/AAAA+QAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAADQAAAA/wAAAP0AAAA8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8AAAA/QAAAP8AAADQAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDAAAA/wAAAP8AAACNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAI0AAAD/AAAA/wAAAIMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAvAAAA+wAAAP8AAADXAAAACQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAA1wAAAP8AAAD7AAAALwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAxAAAAP8AAAD9AAAAOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgAAAD9AAAA/wAAAMQAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASwAAAP8AAAD/AAAAlgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAABYAAAAiAAAAJgAAAB/AAAALwAAAAAAAAAAAAAALwAAAH8AAACYAAAAiAAAAFgAAAARAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlgAAAP8AAAD/AAAASwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMIAAAD/AAAA9AAAABYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEgAAAJQAAAD3AAAA/wAAAP8AAAD/AAAA/wAAAP4AAACQAAAAkAAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA9wAAAJQAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABYAAAD0AAAA/wAAAMIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAD+AAAA/wAAAJQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAOMAAAD/AAAA/wAAAP8AAAD/AAAA9QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPUAAAD/AAAA/wAAAP8AAAD/AAAA4wAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkwAAAP8AAAD+AAAAJwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB5AAAA/wAAAP8AAAAxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAAAAO8AAAD/AAAA/wAAAMkAAABTAAAADwAAAAAAAAArAAAA3gAAAP8AAAD/AAAA3gAAACsAAAAAAAAADwAAAFMAAADJAAAA/wAAAP8AAADvAAAANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADEAAAD/AAAA/wAAAHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAP8AAADhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOQAAAO8AAAD/AAAA/wAAAIMAAAACAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAD/AAAA/wAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAIMAAAD/AAAA/wAAAO8AAAA5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAAAP8AAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAPIAAAD/AAAAoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAdwAAAPcAAAD/AAAA/wAAAHUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAACSAAAA/wAAAP8AAACSAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdQAAAP8AAAD/AAAA9wAAAHcAAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAD/AAAA8gAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB8AAAD/AAAA/wAAAHIAAAAAAAAAAAAAAAAAAAAAAAAAOQAAAJoAAAC5AAAA9AAAAP8AAAD/AAAA/gAAAHEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF8AAAD0AAAA/wAAAP8AAAD/AAAA/wAAAPQAAABfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxAAAA/gAAAP8AAAD/AAAA9AAAALkAAACaAAAAOQAAAAAAAAAAAAAAAAAAAAAAAABxAAAA/wAAAP8AAAAfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5AAAA/wAAAP8AAABVAAAAAAAAAAAAAAAAAAAAAAAAANQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPMAAAABAAAAAAAAAAAAAAAAAAAAAAAAAFIAAAD+AAAA/wAAAP8AAADsAAAA7AAAAP8AAAD/AAAA/gAAAFIAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAPMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAANQAAAAAAAAAAAAAAAAAAAAAAAAAVAAAAP8AAAD/AAAAOQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARQAAAP8AAAD/AAAARQAAAAAAAAAAAAAAAAAAAAAAAAB+AAAA6wAAAN0AAACsAAAArwAAAP8AAAD/AAAAIQAAAAAAAAAAAAAAAAAAAAYAAADlAAAA/wAAAPMAAABQAAAAAQAAAAEAAABQAAAA8wAAAP8AAADlAAAABgAAAAAAAAAAAAAAAAAAACEAAAD/AAAA/wAAAK8AAACsAAAA3QAAAOsAAAB+AAAAAAAAAAAAAAAAAAAAAAAAAEUAAAD/AAAA/wAAAEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEUAAAD/AAAA/wAAAEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD4AAAD/AAAA/wAAAGkAAAAAAAAAAAAAAAAAAABDAAAA/wAAAP8AAABtAAAAAAAAAAAAAAAAAAAAAAAAAG0AAAD/AAAA/wAAAEMAAAAAAAAAAAAAAAAAAABpAAAA/wAAAP8AAAA+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABGAAAA/wAAAP8AAABFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1AAAA/wAAAP8AAABZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAA6wAAAP8AAADLAAAAAAAAAAAAAAAAAAAAZwAAAP8AAAD/AAAAnAAAAIgAAACIAAAAiAAAAIgAAACcAAAA/wAAAP8AAABnAAAAAAAAAAAAAAAAAAAAywAAAP8AAADrAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWQAAAP8AAAD/AAAANQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAAAAP8AAAD/AAAAdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIoAAAD/AAAA/wAAAE4AAAAAAAAAAAAAAEQAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAARAAAAAAAAAAAAAAATgAAAP8AAAD/AAAAigAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHQAAAD/AAAA/wAAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAD3AAAA/wAAAJcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZAAAA8wAAAP8AAADiAAAAEgAAAAAAAAAAAAAAhwAAAPUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD1AAAAhwAAAAAAAAAAAAAAEgAAAOIAAAD/AAAA8wAAABkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACXAAAA/wAAAPcAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1wAAAP8AAAC6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHMAAAD/AAAA/wAAAL4AAAAJAAAAAAAAAAAAAAABAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAAAQAAAAAAAAAAAAAACQAAAL4AAAD/AAAA/wAAAHMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAugAAAP8AAADXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALQAAAD/AAAA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAtQAAAP8AAAD/AAAAwwAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAMMAAAD/AAAA/wAAALUAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANwAAAD/AAAAtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACRAAAA/wAAAPsAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0AAADGAAAA/wAAAP8AAADlAAAAOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAAAAOUAAAD/AAAA/wAAAMYAAAANAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAD7AAAA/wAAAJEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbwAAAP8AAAD/AAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAK0AAAD/AAAA/wAAAPMAAAA1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANQAAAPMAAAD/AAAA/wAAAK0AAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAA/wAAAP8AAABvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwAAAD/AAAA/wAAAEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAAAAagAAAJ8AAACmAAAAgQAAACwAAAABAAAAdgAAAP4AAAD/AAAA4AAAAAwAAAAAAAAAAAAAAAAAAAAAAAAADAAAAOAAAAD/AAAA/gAAAHYAAAABAAAALAAAAIEAAACmAAAAnwAAAGoAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARQAAAP8AAAD/AAAATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApAAAA/wAAAP8AAABoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1AAAA7wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAmwAAAAgAAAB8AAAA/wAAAP8AAAB/AAAAAAAAAAAAAAAAAAAAAAAAAH8AAAD/AAAA/wAAAHwAAAAIAAAAmwAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA7wAAADUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGgAAAD/AAAA/wAAACkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAP0AAAD/AAAAiwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcAAAAP8AAAD/AAAA9wAAAOcAAAD/AAAA/wAAAP8AAACuAAAABAAAANUAAAD/AAAA5wAAAAIAAAAAAAAAAAAAAAIAAADnAAAA/wAAANUAAAAEAAAArgAAAP8AAAD/AAAA/wAAAOcAAAD3AAAA/wAAAP8AAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACLAAAA/wAAAP0AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsAAAD5AAAA/wAAAK4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAADoAAAA/wAAAPMAAABqAAAAgwAAAP4AAAD/AAAA/wAAADsAAABvAAAA/wAAAP8AAAAxAAAAAAAAAAAAAAAxAAAA/wAAAP8AAABvAAAAOwAAAP8AAAD/AAAA/gAAAIMAAABqAAAA8wAAAP8AAADoAAAAEQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArgAAAP8AAADyAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABYAAAA/wAAAP8AAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUQAAAP4AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAOAAAAAWAAAANgAAAP8AAAD/AAAAWgAAAAAAAAAAAAAAWgAAAP8AAAD/AAAANgAAABYAAADgAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD+AAAAUQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAAAAD/AAAA/wAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAsAAAAP8AAAD/AAAA9gAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABZAAAA6QAAAP8AAAD/AAAA+AAAAI8AAAAOAAAAAAAAACQAAAD/AAAA/wAAAGgAAAAAAAAAAAAAAGgAAAD/AAAA/wAAACQAAAAAAAAADgAAAI8AAAD4AAAA/wAAAP8AAADpAAAAWQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAD2AAAA/wAAAP8AAACYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAPgAAAD/AAAA/wAAAP8AAADhAAAAGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAA3AAAAQAAAABAAAAAAAAAAAAAAAAAAAAAjAAAA/wAAAP8AAABpAAAAAAAAAAAAAABpAAAA/wAAAP8AAAAjAAAAAAAAAAAAAAAAAAAAEAAAAEAAAAA3AAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsAAADhAAAA/wAAAP8AAAD/AAAA6wAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEoAAAD/AAAA/wAAAMcAAAD/AAAA/wAAANMAAAARAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAP8AAAD/AAAAaQAAAAAAAAAAAAAAaQAAAP8AAAD/AAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAADTAAAA/wAAAP8AAADTAAAA/wAAAP8AAAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACPAAAA/wAAAP0AAAAUAAAAoQAAAP8AAAD/AAAAwwAAAAkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAAAD/AAAA/wAAAGkAAAAAAAAAAAAAAGkAAAD/AAAA/wAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkAAADDAAAA/wAAAP8AAAChAAAAJQAAAP8AAAD/AAAAfQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0AAAAP8AAADLAAAAAAAAAAUAAAC1AAAA/wAAAP8AAACxAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAA/wAAAP8AAABpAAAAAAAAAAAAAABpAAAA/wAAAP8AAAAjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAACxAAAA/wAAAP8AAAC1AAAABQAAAAAAAADdAAAA/wAAAMEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQAAAPsAAAD/AAAAkAAAAAAAAAAAAAAACwAAAMcAAAD/AAAA/wAAAJwAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAP8AAAD/AAAAaQAAAAAAAAAAAAAAaQAAAP8AAAD/AAAAIwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAACcAAAA/wAAAP8AAADHAAAACwAAAAAAAAAAAAAAoAAAAP8AAAD0AAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADgAAAD/AAAA/wAAAF0AAAAAAAAAAAAAAAAAAAATAAAA1gAAAP8AAAD/AAAAhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAAAD/AAAA/wAAAGkAAAAAAAAAAAAAAGkAAAD/AAAA/wAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEAAAA/wAAAP8AAADWAAAAEwAAAAAAAAAAAAAAAAAAAGsAAAD/AAAA/wAAACsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoAAAA/wAAAP8AAAArAAAAAAAAAAAAAAAAAAAAAAAAAB4AAADjAAAA/wAAAP8AAABsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAA/wAAAP8AAABpAAAAAAAAAAAAAABpAAAA/wAAAP8AAAAjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsAAAA/wAAAP8AAADjAAAAHgAAAAAAAAAAAAAAAAAAAAAAAAA3AAAA/wAAAP8AAABdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAAP8AAAD8AAAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAAO4AAAD/AAAA/QAAAFYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIQAAAP8AAAD/AAAAZwAAAAAAAAAAAAAAZwAAAP8AAAD/AAAAIQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABWAAAA/QAAAP8AAADuAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADwAAAP8AAAD/AAAAhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKwAAAD/AAAA3wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAAA/wAAAP8AAAD4AAAAQwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAC9AAAA4QAAACQAAAAAAAAAAAAAACQAAADhAAAAvQAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABDAAAA+AAAAP8AAAD/AAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADpAAAA/wAAAKQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADMAAAA/wAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM8AAAD/AAAA/wAAAPEAAAAyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyAAAA8QAAAP8AAAD/AAAAzwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyAAAAP8AAADEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4QAAAP8AAACrAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEAAAA/wAAAP8AAAD/AAAA6AAAACMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjAAAA6AAAAP8AAAD/AAAA/wAAAIQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALIAAAD/AAAA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO8AAAD/AAAAlwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATAAAAP8AAAD/AAAA/wAAAP8AAADcAAAAFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXAAAA3AAAAP8AAAD/AAAA/wAAAP8AAABLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAA/wAAAOsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAD8AAAA/wAAAI0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYAAAD/AAAA/wAAAOgAAAD/AAAA/wAAAM4AAAATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATAAAAzgAAAP8AAAD/AAAA6AAAAP8AAAD/AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkAAAAP8AAAD5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAA/wAAAP8AAACIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAA/QAAAP8AAACNAAAAqAAAAP8AAAD/AAAA5QAAAH4AAABVAAAAUQAAAFEAAABRAAAAUQAAAFEAAABRAAAAUQAAAFEAAABRAAAAUQAAAFUAAAB+AAAA5QAAAP8AAAD/AAAAqAAAAI0AAAD/AAAA/QAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkAAAD/AAAA/wAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAP8AAAD/AAAAhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPEAAAD/AAAAngAAAAYAAAC1AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAsAAAAAYAAACeAAAA/wAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACEAAAA/wAAAP8AAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD8AAAA/wAAAI4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADlAAAA/wAAAKcAAAAAAAAAtgAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAI4AAAAAAAAAqAAAAP8AAADoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiwAAAP8AAAD+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9AAAAP8AAACYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5AAAAP8AAAClAAAATQAAAP8AAAD/AAAApgAAAB8AAAA4AAAAOwAAADsAAAA7AAAAOwAAADsAAAA7AAAAOwAAADsAAAA7AAAAOwAAADgAAAAhAAAAywAAAP8AAAD6AAAAKgAAAKkAAAD/AAAA4gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJUAAAD/AAAA+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAAAAD/AAAAqQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOkAAAD/AAAApwAAANsAAAD/AAAA8wAAABsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADkAAAD+AAAA/wAAALsAAAClAAAA/wAAAOoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACjAAAA/wAAAOYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADLAAAA/wAAAMIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD2AAAA/wAAAPYAAAD/AAAA/wAAAHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoQAAAP8AAAD/AAAA4gAAAP8AAAD3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuwAAAP8AAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAswAAAP8AAADcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAA/wAAAP8AAAD/AAAA/wAAANsAAAAHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABkAAADxAAAA/wAAAP8AAAD/AAAA/wAAAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANQAAAD/AAAAuwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAI4AAAD/AAAA+wAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJAAAAP8AAAD/AAAA/wAAAP8AAABNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdQAAAP8AAAD/AAAA/wAAAP8AAAAlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAD1AAAA/wAAAJkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABnAAAA/wAAAP8AAAAqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQAAAD/AAAA/wAAAP8AAAC2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAADYAAAA/wAAAP8AAAD/AAAARAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfAAAA/wAAAP8AAAByAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPwAAAP8AAAD/AAAAVQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABtAAAA/wAAAP8AAAD5AAAAJgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASAAAAP8AAAD/AAAA/wAAAGoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASQAAAP8AAAD/AAAASgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAAD/AAAA/wAAAIUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmQAAAP8AAAD/AAAAigAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACyAAAA/wAAAP8AAACYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAAAD/AAAA/wAAAB4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAAAP8AAAC1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwAAAOwAAAD/AAAA5gAAAA0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIwAAAPgAAAD/AAAA2QAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoAAAA/wAAAO0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALAAAAD/AAAA5gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJUAAAD/AAAA/wAAAF0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACFAAAA/wAAAP8AAABtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2QAAAP8AAAC9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAA/wAAAP8AAAAXAAAAAAAAAAAAAAAAAAAAAAAAAC8AAAD8AAAA/wAAAMUAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAOMAAAD/AAAA7gAAABQAAAAAAAAAAAAAAAAAAAAAAAAADAAAAP0AAAD/AAAAjQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATQAAAP8AAAD/AAAAVgAAAAAAAAAAAAAAAAAAAAEAAADBAAAA/wAAAP0AAAAzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABZAAAA/wAAAP8AAACZAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAD/AAAA/wAAAFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAADyAAAA/wAAAOAAAAAuAAAAAAAAAAQAAACEAAAA/wAAAP8AAACaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAMIAAAD/AAAA/AAAAEUAAAAAAAAAAAAAAAkAAAC9AAAA/wAAAP0AAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdwAAAP8AAAD/AAAA/gAAANsAAADuAAAA/wAAAP8AAADmAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuAAAA+QAAAP8AAAD6AAAArQAAAJcAAADfAAAA/wAAAP8AAACkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAACMAAAA/gAAAP8AAAD/AAAA/wAAAP8AAADgAAAALwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAD7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAADJAAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIAAACOAAAAtAAAAKkAAABqAAAACwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANQAAAK8AAADuAAAA+QAAANIAAAB1AAAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/+P////H////w////8P///+D////wf///4f////h////B////+D///4P////8H///h/////4f//8H/////g///g//////B//+H/4GB/+H//4f+AAB/4f//D/wAAD/w//8P+AgQH/D//w/wPDwP8P/+H8D4HwP4f/4eAfAPgHh//h4B4AeAeH/+HgHAA4B4f/4f4cPDh/h//h/gwAMH+H/+H/DAAw/4f/4f8EACD/h//x/4MAwf+P//H/gf+B/4//8P/A/wP/D//w/+B+B/8P//D8ADwAPw//8PgAPAAfD//w+AAYAB8P//D4ABgAHw//8PwAGAA/D//wfgIYQH4P/+A/Dhhw/Af/4B/+GH/4B//gD/4Yf/AH/+IH/hh/4Ef/wwP+GH/Aw//Dg/4Yf8HD/8PB/hh/g8P/w+D+GH8Hw//H8H4Yfg/j/8f4P//8H+P/x/gf//gf4//H+A//8B/j/4f4B//gH+H/h/gAAAAf4f+H/AAAAD/h/8f8QAACP+P/x/wAAAA/4//H/Af/4D/j/8f8D//wP+P/x/gP//Af4//D+B//+B/D/8P4P//4H8P/w/g///wfw//D+H///h/D/+Pwf//+D8P/4/D///8Px//h4P///weH/+HB////h4f/4IP///+DB//wA////8AP//AH////4A///A/////wH/KAAAADAAAABgAAAAAQAgAAAAAAAAJAAAqA8AAKgPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaQAAAO8AAAAyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyAAAA7gAAAGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAA8wAAAPkAAAAtAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtAAAA+QAAAPMAAAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAADDAAAA/wAAAIQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhAAAAP8AAADDAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHYAAAD/AAAA0AAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAANAAAAD/AAAAdgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKgAAAPYAAAD3AAAAMgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIAAAD3AAAA9gAAACoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAxgAAAP8AAAB/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/AAAA/wAAAMYAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABmAAAA/wAAAM0AAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAUAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAzQAAAP8AAABmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcAAADeAAAA/gAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEEAAACmAAAA3gAAAOoAAADEAAAARgAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABiAAAA/wAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAADxAAAA/wAAAPQAAAA9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9AAAA9AAAAP8AAADxAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjQAAAP8AAABdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxAAAA/wAAAHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAA/wAAAP8AAADsAAAALQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0AAADsAAAA/wAAAP8AAAC/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAeAAAAP8AAABvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/AAAA/wAAAGkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYAAAA/wAAANkAAAD/AAAA4wAAAC4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALgAAAOMAAAD/AAAA2QAAAP8AAACUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAawAAAP8AAAB9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAAAA/wAAAGQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB7AAAA/wAAAHQAAACjAAAA/wAAAPkAAADKAAAAvAAAALwAAAC8AAAAvAAAALwAAAC8AAAAvAAAALwAAADKAAAA+QAAAP8AAACiAAAAdAAAAP8AAAB6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZQAAAP8AAACCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB+AAAA/wAAAGkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABtAAAA/wAAAHwAAAA9AAAA/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPsAAAAnAAAAfQAAAP8AAABvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZwAAAP8AAAB/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB1AAAA/wAAAHMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsAAAA/wAAAH8AAADIAAAA/wAAAGwAAAAjAAAALAAAACwAAAAsAAAALAAAACwAAAAsAAAALAAAACwAAAAjAAAAiQAAAP8AAACuAAAAgAAAAP8AAABrAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcQAAAP8AAAB4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAA/wAAAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABzAAAA/wAAANQAAAD/AAAAzwAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQAAAOQAAAD+AAAAvQAAAP8AAAB1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgwAAAP8AAABkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABKAAAA/wAAAKEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACFAAAA/wAAAP8AAAD9AAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFsAAAD/AAAA/wAAAP8AAACEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAAAAP8AAABPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAAAA/gAAAMYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACfAAAA/wAAAP8AAAClAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAADBAAAA/wAAAP8AAACfAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAvgAAAP8AAAAuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAA9AAAAOsAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADBAAAA/wAAAPEAAAAeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzAAAA+gAAAP8AAADBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAA5QAAAPcAAAAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0wAAAP0AAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAUAAADoAAAA/wAAAHsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAAAAP8AAADnAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA+gAAANwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAogAAAP8AAABOAAAAAAAAAAAAAAAAAAAAAAAAAFMAAAD/AAAA2wAAAAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAO0AAAD+AAAAOQAAAAAAAAAAAAAAAAAAAAAAAABFAAAA/wAAAKwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcgAAAP8AAAB/AAAAAAAAAAAAAAAAAAAACQAAAN4AAAD+AAAATgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGwAAAD/AAAAxwAAAAIAAAAAAAAAAAAAAAAAAAB1AAAA/wAAAHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAP8AAAC3AAAAAAAAAAAAAAAAAAAAfgAAAP8AAAC2AAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAADQAAAA/wAAAF8AAAAAAAAAAAAAAAAAAACoAAAA/wAAAEsAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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"""
icondata = base64.b64decode(icon)
tempFile = "icon.ico"
iconfile = open(tempFile, "wb")
iconfile.write(icondata)
iconfile.close()
window.wm_iconbitmap(tempFile)
os.remove(tempFile)
testCode()
logout()
window.mainloop()
