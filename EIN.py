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
"""AAABAAUAEBAAAAEAIABoBAAAVgAAABgYAAABACAAiAkAAL4EAAAgIAAAAQAgAKgQAABGDgAAMDAA
AAEAIACoJQAA7h4AAJycAAABAAgAaG8AAJZEAAAoAAAAEAAAACAAAAABACAAAAAAAAAEAAAAAAAA
AAAAAAAAAAAAAAAA9vb2/+Dj5f+mrrT/tLSz/+np6P/v7+//9/f3/+Li4v+vraz/p6al/6OkpP+4
t7b/4eHh//f39//29vb/9fX1//r5+f+wvcb/PYnE/3qFjf+QlZj/lZmd//Lx7//S0M//hKS8/26K
oP9Mf6X/epmx/7y7u//4+Pj/9vb2//b29v/6+vn/rrnB/wl1yP8lZJb/LlZ1/0Zbav+Up7b/WYer
/xJutv8eidv/S3eb/zZkif+ys7T/+Pf3//b29v/29vb/+Pj4/8rMzv8deL7/Ao77/wRzy/8HS4D/
Bn3a/wOL9v8FaLb/EIzs/6jS8v/g3t3/l5eX/9XV1f/4+Pj/9vb2//r5+P+1wMj/DoDa/wOS//8E
kv//BYXn/wSP+f8Ekv//BY74/wGO/P88qf7/6fT9/9zb2/+zs7P/9PT0//b29v/6+vn/rbW8/wh0
xv8Ek///BJH//wSS//8Ekf//BJL//wSR//8Fkf//Yrn8/+71+v/y8vL/paWl/+7u7v/29vb/+fn5
/8XExP8xc6f/A5D8/wKR//8Aj/3/Aonz/wOG6/8Bj/3/NKX9/9/u+f/9/Pv/z8/Q/6urq//29vb/
9vb2//j4+P/HxsX/g56y/xVsr/8kf8b/SYe3/3CZuf9ohZz/B3jQ/124/v/6+vn//fz7/6inp/++
vr7/+Pj4//b29v/4+Pj/zc3N/3CAjP+gp6z/1dfY/+/s6//39fP/2dfV/ylhjf8cl/f/h8r9/9Hj
8P+urq3/n5+f/9ra2v/29vb/9vb2//Dw8P/Z2dj/9vX1//j4+P/29vb/+Pj4/9DR0f8caaX/AJD/
/wWS//8om/P/o8vq/+7u7v+kpKT/7Ozs//b29v/29vb/9/f3//b29v/29vb/9vb2//n5+f+us7f/
JWme/xeE2f8Dkf//AHXR/0mLvv+nq63/hoWF/+3t7f/29vb/9vb2//b29v/29vb/9vb2//b29v/3
9vb/iZag/5Gqvf9nkLH/AYHl/yWZ8/9km8X/vL2+/+7u7v/19fX/9vb2//b29v/29vb/9vb2//b2
9v/29vb/7Ozs/6anqP/u7/D/dJCm/yJejv8mfL7/boeZ/+vp6P/39/f/9vb2//b29v/29vb/9vb2
//b29v/29vb/9vb2//Dw8P++vr7/ysrK/8rIxv94kKT/AXTM/5Opuf/6+fj/9vb2//b29v/29vb/
9vb2//b29v/29vb/9vb2//b29v/29vb/5+fn/9TU1P/39vb/ztPX/yt1rv+gtML/+vn4//b29v/2
9vb/9fX1//b29v/29vb/9vb2//b29v/29vb/9vb2//f39//39/f/9vb2//Pz8/++xsz/4eTm//f3
9//29vb/9fX1/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAoAAAAGAAAADAAAAABACAAAAAAAAAJAAAAAAAAAAAAAAAAAAAAAAAA
8/Pz//j4+P/v7+//x8fH/7q6uv/Q0ND/9vb2//v7+//39/f/9/f3//X19f/q6ur/v7+//729vP++
vr7/vby8/7y8vP/CwsL/7e3t//b29v/29vb/9fX1//f39//09PT/9/f3//j39/+wt73/UX+i/5ui
p/+DgoL/zMzM/8XExP/S0tL/9PT0//n5+f/Jycn/hIOD/62trP91dXT/Xmpz/62ws/+pqaj/srKy
//b29v/19fX/9vb2//X19f/39/f/9fX1//r6+f+Rm6T/D3/T/1SVxv98e3r/fX+A/3+Mlf9xcnL/
8fHx//v7+v/Jx8X/fpqu/3jA9/9ufYn/JWWV/1+3+f9mfIz/lJOS//f39//29vb/9fX1//b29v/1
9fX/9vb2//r5+P+SnKT/A3nU/wdsu/9KWGP/QlZm/zBunf9wc3X/0M7N/7u/w/9ec4T/FGWi/waT
//8cecD/LFBs/wdfpf8VT3z/vbu6//r6+v/29vb/9vb2//b29v/29vb/9vb2//r5+f+foaT/DF6d
/wSP+v8Ec8r/BlWU/wYmQP8XMEP/H2ii/xlxt/8Fg+X/CFON/wRsvf8fnv//uc7d/56hpP+Jj5T/
bGtr/9LS0v/4+Pj/9vb2//b29v/29vb/9vb2//f39//T0tH/Kmma/wKQ/v8Ekv//BZH7/wduvf8H
T4j/BIz1/wOS//8Ek///BnXL/wZmsP8Fk///gsf9//39/P/9/fz/s7Oz/3x8fP/x8fH/9vb2//b2
9v/29vb/9vb2//n5+P+dpaz/C3fL/wSS//8Ekf//BJH//wSQ+/8Hdcr/BY76/wSR//8Ekf//BY/6
/wWM9v8Dkf//G5v+/7Da+v/8+/r/8vLy/4eHh//Hx8f/+Pj4//b29v/29vb/9fX1//r6+f+RnKT/
A3jR/wST//8Ekf//BJH//wSR//8Ekv//BJH//wSR//8Ekf//BJH//wSR//8Ekf//AZD//4XI+//8
+vn/+/r6/+Hh4f+ampr/9PT0//b29v/19fX/9/f3//n5+P+Slpn/BF2h/wSS//8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Fkf//U7L8/93t+f/6+vn/+/v7/8XFxf+FhYX/9fX1
//X19f/29vb/9PT0//r6+v+ysK7/HVJ6/wOP+v8Ekf//BJH//wSR//8Ekf//BJL//wOS//8Ek///
BJH//wKQ//8pof7/1ur6//z6+f/5+fn//Pz8/5+fn/+3t7f/+Pj4//b29v/19fX/9/f3//f39/+0
s7P/iJWf/x97w/8DkPz/A5P//wKJ8f8Bhez/CH/c/xdqqv8MZ67/BIvz/wKQ//96w/v/+fn5//n5
+f/7+/v/zMzM/2dnZ//c3Nz/+Pj4//X19f/39/f/9PT0//r6+v+kpKP/vMbN/zp1ov8NWJL/Fmuu
/096m/9lgJX/f5Oj/8bGxv92en3/CmWr/wGS//+Hyfv///z5//r5+f/7+/v/zc3N/4KCgv/v7+//
9vb2//f39//09PT/+Pj4//f39/+qqan/epGh/z1VaP+rqqn/xcXF/+bl5P/49vX/9vTz//v7+//Y
1tb/Mk1i/wN51f8wpf//o9X6/+r0+//19PL/qaio/3R0dP+BgYH/5OTk//b29v/39/f/8/Pz//n5
+f/b29v/hIWG/7u7u//7+/v/+Pj4//j4+P/19fX/9/f3//f39//S0tH/LE1o/wV+3f8Ckf//DJT+
/0au/v+Txev/rbW6//T08//Jycn/rKys/+Tk5P/19fX/+Pj4//T09P/4+Pj/8vHx//j4+P/09PT/
9/f3//T09P/39/f/9fX1//r5+f/Ix8b/GFF9/wSQ+f8Ekf//A5H//wGQ//8Lkvv/cLz3/+/2+//+
/f3/j4+P/76+vv/7+/v/8/Pz//j4+P/09PT/+Pj4//T09P/39/f/9PT0//f39//09PT/9/f3//f3
9/+rq6z/El6Z/wp60f8Fj/j/BJH//wST//8FYar/G2Ob/7bQ4v+2tLP/Pj4+/729vf/4+Pj/+fn5
//T09P/4+Pj/9PT0//j4+P/09PT/9/f3//T09P/39/f/9fX1//j39/9jbHL/Jl6J/46frP8cZqD/
A475/wOS//8De9n/IIXU/3+Yqv+Zl5b/tbW1/+Xl5f/5+fn/8/Pz//j4+P/09PT/+Pj4//T09P/4
+Pj/9PT0//f39//09PT/+Pj4/+jn5v9YbHz/jbDL/+Xo6v9Gc5f/AoPo/wuS/P9CrP3/frPb/4iQ
lf/r6+v/+fn5//j4+P/z8/P/+fn5//T09P/4+Pj/9PT0//j4+P/09PT/+Pj4//T09P/39/f/9/f3
/8XFxf+LjY3/9/j5/9fe4/8ta5z/HFaF/xJWjf9NkML/Sm+M/6yqqf/4+Pj/9/f3//T09P/4+Pj/
8vLy//j4+P/z8/P/+Pj4//T09P/4+Pj/9PT0//f39//09PT/+vr6/8TExP+xsbH//////8jHx/+I
iYr/bnmC/wRsvf8AfuD/Tmh8/+no5//4+Pj/9fX1//f39//z8/P/+fn5//Pz8//4+Pj/9PT0//j4
+P/09PT/+Pj4//T09P/39/f/9vb2/+Li4v+srKz/xMTE/7CwsP/v7+7/t7a1/xVfmP8Aguf/dYuc
//n49//19fX/9/f3//T09P/4+Pj/8vLy//j4+P/z8/P/+Pj4//T09P/4+Pj/9PT0//f39//09PT/
9/f3//b29v/d3d3/sbGx/+rq6v/39/f/7evq/1yDov8AddH/b4aY//f29f/39/f/9fX1//f39//z
8/P/+fn5//Pz8//4+Pj/9PT0//j4+P/09PT/+Pj4//T09P/39/f/9PT0//f39//29vb/+fn5//b2
9v/29vb/+Pj4/7i+w/9BcJX/rLa+//j49//19fX/9/f3//T09P/4+Pj/8fHx//n5+f/z8/P/+fn5
//Pz8//4+Pj/8/Pz//j4+P/09PT/+Pj4//T09P/39/f/9PT0//b29v/19fX/9vb2//X09P/i4N7/
9PPz//X19f/39/f/9PT0//j4+P/y8vL/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAKAAAACAAAABAAAAAAQAgAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAPT09P/29vb/9vb3
//X19f/o5uX/4ODf/+Dg4P/s7Oz/9fX1//X19f/39/f/9PT0//b29v/29vb/9PT0//Ly8v/j4+P/
39/f/+Dg4P/g4OD/4uLi/+Dg4P/f39//4uLi//X19f/09PT/9/f3//b29v/09PT/9/f3//X19f/1
9fX/8PDw//f39//5+fn/yczO/2R3hf93eHj/aWlo/5CQkP/39/f/9/f3//z8/P/09PT/9/f3//j4
+P/09PT/zMzM/2FhYf94eHj/fHx8/29vb/9YWFf/e3p5/3h3d/+AgID/xcXF//Hx8f/5+fn/9vb2
//Ly8v/6+vr/9PT0//Pz8//9/f3/9PT0//X19P96g4r/G3jA/6bT9P+7u7z/eHh4/6Kiov+Eg4P/
g4KC/6anp//z8/P/8vLy//////+6urr/iIiH/+vw8/+7vsH/bGpp/z1Zbv+62e//5+rs/9HQ0P94
eHj/9PT0//Ly8v/29vb/+vr6//Dw8P/5+fn/+fn5//Hx8f/39/f/+/r6/3N7gv8Acsn/H5r6/z9a
bv+Mion/dHNy/5ynr/99iZH/ZWRk//T09P/4+Pj/+Pj4/8HBwP9ugI7/YLr//2Kr5P99goX/FEtz
/yej//9ClNT/QExV/3Rzc//u7u7/+fn5//b29v/z8/P/+fn5//T09P/09PT/9PT0//b29v/5+fj/
dH2D/wJzyv8BjPj/HURi/3h3dv9HTlT/UqHc/yJQc/+Rj43/8O7t//Hw7/+4ubv/amxv/xRWif8F
k///CZT+/xdgmf8SMkz/CFiY/wF/4f8ZSnH/x8XD//f39//39/f/9vb2//X19f/39/f/9fX1//X1
9f/8/Pz/9PT0//b19f93fYL/A2Ww/wWR/f8HeND/B0h8/wYiOv8HOF7/DRkj/0VLUf9NY3b/TWN1
/ypsoP8Fbb7/ClKL/whqt/8CkP//IZn1/625wf9kZmj/M1Rt/zNCTv9ra2r/6Ojo//Pz8//29vb/
+vr6//Dw8P/4+Pj/+fn5/+/v7//39/f/+/v7/6KhoP8aQV//BIv0/wST//8Gjvf/CInv/whWk/8G
Ijf/BTZd/wWC5f8EhOj/BIz1/wSV//8HaLH/BzNW/wSI7/8Zmv//st39//Hw7//o5uX/39/e/2pq
av9lZWX/6urq//f39//y8vL/+/v7//Pz8//z8/P/+Pj4//X19f/29vb/3Nzb/zRggv8CivT/BJH/
/wSR//8Ekv//BoTl/whzxf8HR3n/BZD7/wSS//8Ekf//BJH//wWM9f8IT4f/BYju/wCQ//9Ws/z/
8Pb6//v7+v/7+/v/6Ojo/2BgYP+xsbH/9/f3//f39//09PT/9/f3//f39//6+vr/9fX1//f29v+E
i5H/CnDB/wSS//8Ekf//BJH//wSR//8Ekv//Bofr/whjqv8FkPz/BJH//wSR//8Ekf//BJD+/waJ
8P8EkP3/A5H//w2V/v99xfv/8PX5//r5+f/8/Pz/oaGh/19fX//s7Oz/+fn5//Pz8//39/f/+Pj4
/+/v7//39/f//Pv7/3J6gf8Ccsn/BJP//wSR//8Ekf//BJH//wSR//8Ekf//BZH//wSR//8Ekf//
BJH//wSR//8Ekf//BJL//wSR//8Ekf//AZD//yCc/v/a7Pn/+/r5//n5+f/29vb/qKio/6urq//z
8/P//Pz8//Pz8//y8vL/+/v7//T09P/29vX/d3+G/wJyyf8Ek///BJH//wSR//8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8CkP//Sa/8/+Xx+f/6+vn/+fn5
//39/f/CwsL/i4uL//z8/P/x8fH/+Pj4//j4+P/19fX/9vb2//n4+P90dnj/A0V4/wWP+v8Ekf//
BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BZH//0it/P/U
6vn/+vr5//n5+f/5+fn/8/Pz/3d3d/+Hh4f/+Pj4//b29v/29vb/9fX1//Hx8f/39/f/+vr6/5SS
kf8RM0z/BIz0/wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH/
/wKQ//8hnf7/zuf6//z6+f/5+fn/+fn5//r6+v/r6+v/a2tr/9TU1P/09PT/+vr6//T09P/09PT/
/f39//T09P/09PT/uLe3/259iP8Wc7z/BJD8/wSR//8Ekf//BJL//wST//8Ek///BJL+/wSJ8f8E
h+3/BYz0/wSS//8Ekf//BpL//3PA+//y9vn/+vn5//n5+f/5+fn/9/f3/6Wlpf9dXV3/7e3t//v7
+//w8PD/+fn5//n5+f/x8fH/9/f3//r6+v+CgoL/v768/3OPpv8Hbr3/BJL9/wST//8Fhun/BHHF
/wNwxf8LcL//OWGB/zxVaP8RPmL/Bn/c/wSS//8Jk/7/s9v6//37+f/5+fn/+fn5//v7+//W1tb/
RUVF/6ysrP/29vb/8/Pz//n5+f/09PT/9PT0//T09P/29vb/+Pj4/4ODg//HyMf/hcDs/wY4YP8P
UIP/DleP/ztpjf9+hYr/f4aM/4mPlP/b2tr/5+bk/3h2df8LUYb/BJL//wmT//+s2fr//vv5//r5
+f/5+fn/+vr6//b29v95eXn/vr6+//b29v/19fX/9/f3//X19f/19fX//Pz8//T09P/19fX/iYeH
/5+ywP8yZYz/QUhO/66sq/+6uLf/0dDP//T09P/9/f3/9/f3//T09P/+/v7/zMvL/ys9S/8HaLT/
BJD+/0Wt/f/B4fn/7fX6//78+v/49/f/wMDA/1hYWP9VVVX/iYmJ//Ly8v/x8fH/+Pj4//n5+f/v
7+//9/f3//r6+v+vr6//bXBy/0ZKTv/Ly8r//v7+//f39//29vb/+/v7//Hx8f/39/f/+fn5//Ly
8v/g4OD/T1FT/whJe/8Fjvj/BZL//xWY/f9mvPz/uOD8/+Hk5v+BgYD/4+Pj/83Nzf+BgYH/pqam
//Pz8//09PT/8/Pz//j4+P/19fX/9fX1//X19f+4uLj/0NDQ//r6+v/09PT/9/f3//b29v/09PT/
+Pj4//X19f/09PT/+/v7/7++vf8UOlf/B4Pj/wSS//8Ekf//A5H//wGQ//8cm/7/U6/1/6bB1P/6
+fj/+vr6//r6+v+zs7P/nZ2d//j4+P/39/f/+fn5//X19f/09PT/+fn5//f39//4+Pj/+Pj4//Pz
8//39/f/9vb2//Pz8//4+Pj/9fX1//T09P/8/Pz/v769/xQ4VP8HguH/BJL//wSR//8Ekf//BJH/
/wKQ//8CkP7/P6r9/8zm+v/8+/r/+vr6/5qamv93d3f/+fn5//f39//v7+//9/f3//n5+f/w8PD/
+vr6//b29v/x8fH/+/v7//Pz8//09PT/+/v7//Dw8P/39/f/+fn5//Ly8v+zsrD/EVaL/wOE6P8D
iO3/BJL//wSR//8Ekf//BJL//whXlv8FS4P/iMb1/+nn5f/V1dX/ODg4/21tbf/19fX/8/Pz//z8
/P/09PT/8/Pz//v7+//y8vL/9vb2//r6+v/x8fH/+Pj4//f39//x8fH/+vr6//X19f/z8/P/8fHx
/0tKSf8ISXv/SHme/zxtk/8GhOb/BJL//wSR//8Ekv//CVeV/wZMgv99vOv/bWtq/3Nzc/9fX1//
mZmZ//r6+v/5+fn/9fX1//b29v/29vb/9fX1//b29v/29vb/9fX1//f39//19fX/9vb2//f39//1
9fX/9vb2//f39//q6ej/N0tb/xpZi//H09z/oZ+e/w8/Zf8FivH/BJH//wOQ//8EkP3/F5n9/324
5P+Bf37/5ubm//Pz8//29vb/9fX1//X19f/x8fH/9/f3//j4+P/y8vL/+fn5//b29v/z8/P/+vr6
//T09P/09PT/+fn5//Ly8v/39/f/+fn5/8TCwf83T2L/jbrd//Ty8P/L3Oj/MGWP/wOG6/8Ekv//
HZz+/1q2/f+tz+n/aHF4/728vP/29vb/8/Pz//r6+v/09PT/9PT0//39/f/09PT/8/Pz//z8/P/x
8fH/9vb2//v7+//w8PD/+fn5//j4+P/w8PD/+/v7//T09P/09PT/hYWF/4mKiv/19vf//v38/5ix
xv8NbLf/E1eN/wlLgf8tX4b/cqfO/1mMsf9cXV7/39/f//f39//6+vr/8PDw//n5+f/5+fn/8fHx
//f39//4+Pj/8vLy//n5+f/29vb/8/Pz//r6+v/09PT/9PT0//n5+f/y8vL/9/f3//n5+f+Ghob/
ycnJ//7+/v/+/v7/lJSV/0VTXv90dnj/Ck+G/wZ3z/8DfNr/Ez1c/6GgoP/9/f3/9vb2//Pz8//6
+vr/9PT0//T09P/09PT/9vb2//f39//19fX/9/f3//b29v/19fX/9/f3//X19f/19fX/9/f3//X1
9f/29vb/+Pj4/4yMjP/Gxsb//////+Pj4/+UlJT/0M/O/6Sko/8NQWv/BYz0/wGE6P9JYnT/7Orp
//f39//29vb/9fX1//f39//19fX/9fX1//z8/P/09PT/8/Pz//v7+//y8vL/9vb2//r6+v/x8fH/
+Pj4//f39//x8fH/+vr6//X19f/09PT/2dnZ/5qamv/Dw8P/mJiY/87Ozv/7+/v/5OPi/0VVYv8C
f97/AYTp/05mef/19PP/8vLy//b29v/6+vr/8fHx//j4+P/5+fn/7+/v//f39//5+fn/8PDw//r6
+v/29vb/8fHx//v7+//z8/P/9PT0//v7+//x8fH/9/f3//n5+f/y8vL/1dXV/4qKiv/MzMz//f39
//Pz8//19fT/m6Kp/xVusv8Ag+b/S2N2/+vp6P/6+vr/9vb2//Hx8f/7+/v/8/Pz//Pz8//4+Pj/
9fX1//T09P/4+Pj/9PT0//b29v/4+Pj/8/Pz//f39//29vb/8/Pz//j4+P/19fX/9PT0//j4+P/1
9fX/9/f3//j4+P/z8/P/9/f3//j4+P/g3tz/PWOB/wRuv/9gdIT/9PLx//T09P/29vb/9/f3//Pz
8//39/f/9/f3//n5+f/19fX/9fX1//j4+P/09PT/9vb2//j4+P/z8/P/9/f3//f39//z8/P/+Pj4
//X19f/09PT/+Pj4//T09P/29vb/+Pj4//Pz8//39/f/9/f3//Pz8/++wsX/doCI/9TW2P/5+fn/
9PT0//b29v/4+Pj/8/Pz//f39//39/f/7e3t//j4+P/6+vr/7u7u//v7+//29vb/8PDw//39/f/y
8vL/8/Pz//z8/P/v7+//+Pj4//r6+v/u7u7/+/v7//b29v/w8PD//f39//Ly8v/09PT//Pz8//Dw
8P/4+Pf/+vr6/+/v7//7+/v/9vb2//Dw8P/9/f3/8vLy//Ly8v8AAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAw
AAAAYAAAAAEAIAAAAAAAACQAAAAAAAAAAAAAAAAAAAAAAAD4+Pj/+Pj4//T09P/z8/P/9/f3//j4
+P/4+Pj/+Pj4//v7+//9/f3/+vr6//X19f/29vb/+Pj4//X19f/z8/P/9vb2//j4+P/29vb/8/Pz
//X19f/4+Pj/9vb2//T09P/5+fn//Pz8//v7+//4+Pj/+Pj4//z8/P/8/Pz/+Pj4//j4+P/8/Pz/
/Pz8//j4+P/09PT/9/f3//j4+P/19fX/8/Pz//f39//4+Pj/9fX1//Pz8//29vb/+Pj4//b29v/t
7e3/7+/v//v7+//9/f3/8fHx/+7u7v+8u7r/paWk/5+fn/+cnJz/pKSk/93d3f/29vb/7e3t//b2
9v/+/v7/9vb2/+zs7P/19fX//v7+//j4+P/t7e3/9PT0/+Xl5f+oqKj/nZ2d/5+fn/+lpaX/pKSk
/56env+goKD/paWl/6SkpP+enp7/nZ2d/6urq//u7u7/8vLy/+3t7f/6+vr//v7+//Ly8v/t7e3/
+Pj4//7+/v/19fX/7e3t//X19f/x8fH/8vLy//n5+f/6+vr/8PDw/7Gztf84WHH/S1Zf/2RjYv9h
YWH/KCgo/5ubm//8/Pz/9vb2//r6+v/+/v7/+vr6//Pz8//19fX/+vr6//f39//x8fH/+Pj4/7Ky
sv8oKCj/X19f/2JiYv9jY2P/Z2dn/1ZWVv8gIB//XFpZ/2NjYv9iYmL/YWFh/2lpaf+oqKj/5OTk
//Pz8//4+Pj/+vr6//T09P/x8fH/9/f3//r6+v/19fX/8fHx//b29v/+/v7//Pz8//Dw8P/v7+//
8fHx/0JITP8Lbrz/gMb7/+Xx+P/8+vn/YmJi/5KSkv/Ozs7/qqqq/6Wlpf+hoaH/pqam/9PT0//4
+Pj/7e3t//T09P/+/v7//Pz8/6ioqP9UVFT/8/Ly//37+f/r6un/rq6u/4uLi/8xOD3/psjh//P3
+f/8+vj//Pz8/+vr7P9NTU3/ycnJ///////y8vL/7e3t//n5+f/+/v7/8/Pz/+3t7f/39/f//v7+
//b29v/7+/v/+vr6//Pz8//y8vL/8O/v/0BFSf8DbL7/C5X//4HF+f+5xc3/R0ZG/5WVlf9xcXH/
MTEx/1hXVv9aWVj/Li4u/3Z2dv/6+vr/8fHx//X19f/7+/v/+/v7/6qqqv9WVVX/5O30/7je+/+l
w9r/YmJj/0pJSP8NIzT/Ho/k/6DU+/+22fP/ur7C/62sq/88PDz/x8fH//39/f/09PT/8fHx//j4
+P/7+/v/9PT0//Hx8f/39/f/+/v7//b29v/u7u7/7+/v//v7+//9/f3/6ejo/zxBRf8DbL7/BJP/
/wqS+/8PPV//Ojc2/729vf9ycnL/kpGQ/9bs+v+2y9n/YGBf/21tbf/4+Pj//v7+//f39//v7+//
+vr6/7Oysv9ETVT/icf0/xCW/v8wovv/rNDr/52cnP8YLj7/BYbl/wqW//8Oje//FENq/xIWGf9N
TEz/0NDQ//Dw8P/6+vr//v7+//Pz8//u7u7/+Pj4//7+/v/19fX/7e3t//X19f/w8PD/8vLy//r6
+v/7+/v/6urp/z1CRv8DbL7/BJP//wSQ/P8JOFv/f3t4/8PCwf9WVlb/dIeV/2C///8LUob/KCYl
/5eXl//7+/v//v7+//v7+//f3t7/vry7/4qGhP8NNFL/CpH4/wOR//8Fk///DoPe/w4vSf8GGCf/
CWOs/wp1yv8Fj/n/CITm/xktPf/My8r/9fX1//Hx8f/5+fn/+/v7//T09P/w8PD/+Pj4//v7+//1
9fX/8PDw//b29v/9/f3//Pz8//Hx8f/w8PD/8fHw/0BFSf8Dbb7/BJT//wSQ/f8JTYH/EC1E/xAa
Iv8FBAL/EEhz/w97zf8GPGX/ZmVk/8jHxv/Fw8L/v728/8bDwv+OmKD/FjVN/xAtRf8MQGn/CnzT
/wSS/f8Ekf//A5H//xGC2f8/TFb/PT9C/woaKP8HZq7/B2q3/xMjMP+ko6L/9PT0//7+/v/y8vL/
7u7u//n5+f/9/f3/8/Pz/+7u7v/39/f//v7+//b29v/8/Pz/+/v7//Hx8f/x8fH/8PDw/z9DRv8H
WJj/Boz0/wSR//8Gjvf/CIzy/wpLf/8IIDX/CilD/wgbLP8DBQj/CwkI/xYiLP8aNEr/GTNJ/xky
R/8XV4n/B4vx/waN9f8Ka7X/CixI/wp50f8EkP3/AZD//y2h/P/g6vL/3Nva/09QUP89Q0j/PkVK
/zg5Ov8nJyf/q6ur//b29v/09PT/7+/v//n5+f/8/Pz/9PT0/+/v7//39/f//Pz8//b29v/v7+//
8PDw//v7+//9/f3/6+vr/11cXP8OGCH/B3DB/wST//8Ekf//BJH//weN9v8JivD/Cozz/whBbv8E
Dhb/BA4W/whBbv8Ji/L/CInv/wiJ7/8GjPX/BJH//wST//8Idsr/Bxwt/wYtTP8Gjfb/ApD//yaf
/v/E4/r/9ff4/+7u7v/t7Oz/7e3t/+Li4v9ZWVn/Hh4e/6CgoP/y8vL//f39//Pz8//v7+//+Pj4
//39/f/19fX/7u7u//X19f/v7+//8PDw//r6+v/8/Pz/8vLy/9/f3v9BRkr/BGu6/wST//8Ekf//
BJH//wSR//8Ekf//BZP//wlUjv8LWJT/CUp9/wdEdP8FlP//BJH//wSR//8Ekf//BJH//wSR//8F
kf3/Cmew/wYrSP8GjPT/BJH//wWR//88p/z/5fH6//v6+v/6+vr/+vr6//r6+v/l5eX/WVlZ/yQk
JP/Hx8f///////Pz8//v7+//+Pj4//39/f/19fX/7+/v//b29v/8/Pz/+/v7//Hx8f/w8PD/+fn5
/93d3v9BU2P/BXHE/wST//8Ekf//BJH//wSR//8Ekf//BJH//waM9P8Gj/j/Bk6F/wdEdP8Fk///
BJH//wSR//8Ekf//BJH//wSR//8Ek///B3PI/wk7ZP8Gjfb/BJH//wKQ//8knf3/xeP6//j5+f/6
+fn/+fn5//n5+f/5+fn/4eHh/0BAQP+fn5//6urq//n5+f/8/Pz/9PT0/+/v7//39/f//Pz8//b2
9v/9/f3//Pz8//Hx8f/w8PD/8vLx/1RYXP8Oa7T/Bo/7/wSR//8Ekf//BJH//wSR//8Ekf//BJH/
/wSR//8Ek///CViW/wlPh/8Fk///BJH//wSR//8Ekf//BJH//wSR//8Ekf//Bo74/wiI7f8Ekf7/
BJH//wSR//8Gkv//MKT8/8jl+f/2+Pn/+fn5//n5+f/6+vr/8fHx/1VVVf8iIiL/uLi4//39/f/9
/f3/8/Pz/+7u7v/39/f//v7+//b29v/w8PD/8vLy//r6+v/7+/v/6urp/z1CRv8Dbb7/BJP//wSR
//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//CIvy/weK7/8Ekf//BJH//wSR//8Ekf//BJH/
/wSR//8Ekf//BJH//wSS//8Ekf//BJH//wSR//8Ekf//BZH//zmm+//e7fn/+/r5//n5+f/5+fn/
+Pj4/+Dg4P9hYWH/ra2t/+/v7//x8fH/+Pj4//z8/P/19fX/8PDw//b29v/u7u7/7+/v//v7+//9
/f3/6ejo/zxBRf8DbL7/BJP//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//ApD/
/yCc/v/Z6/n/+/r5//n5+f/5+fn/+fn5//r6+v/i4uL/Y2Nj/7Ozs//x8fH/+Pj4//7+/v/19fX/
7e3t//X19f/7+/v/+vr6//Pz8//y8vL/8O/v/0BFSf8Dbb7/BJP//wSR//8Ekf//BJH//wSR//8E
kf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//BJH//zGk/P/c7fn/+/r5//n5+f/5+fn/+fn5//n5+f/19fX/UFBQ
/6+vr///////9PT0//Hx8f/39/f/+/v7//b29v/+/v7//Pz8//Dw8P/v7+//8fHx/0BFSf8GZrH/
BZH9/wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8E
kf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Fkf//LKL8/7/i+v/19/n/+fn5//n5
+f/5+fn/+fn5//n5+f/p6en/S0tL/7Gxsf//////8/Pz/+3t7f/39/f//v7+//b29v/x8fH/8vLy
//n5+f/6+vr/6+rq/zw9Pf8DGiz/CHbL/wST//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//
BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wWR//8x
o/z/weH5//f4+f/6+fn/+fn5//n5+f/5+fn/+fn5//T09P9ubm7/HBwc/7CwsP/19fX/9/f3//r6
+v/19fX/8fHx//X19f/t7e3/7+/v//v7+//+/v7/6enp/0ZGRf8DCAz/B269/wST//8Ekf//BJH/
/wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//
BJH//wSR//8Ekf//ApD//yWf/v/A4vr/+Pn5//r5+f/5+fn/+fn5//n5+f/5+fn/+vr6//Ly8v9R
UVH/kZGR/+bm5v/u7u7/+Pj4//7+/v/19fX/7e3t//X19f/5+fn/+fn5//Pz8//z8/P/9vb2/8nJ
yP9ARUn/C2y3/wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH/
/wSR//8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//zim/P/p8vn/+/r5//n5+f/5+fn/
+fn5//n5+f/5+fn/+fn5/+zs7P9RUVH/tLS0//z8/P/5+fn/9fX1//Ly8v/39/f/+fn5//b29v/+
/v7//f39//Dw8P/u7u7/9PT0/3x8fP+hoqP/SWF2/wpwwf8Gkv//BJH//wSR//8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//BpD8/wiO9/8Ijvf/CI73/weP+v8Ekf//BJH//wSR//8CkP//Jp/9
/7vf+f/2+Pn/+fn5//n5+f/5+fn/+fn5//n5+f/5+fn/7u7u/2pqav8gICD/sbGx//39/f/+/v7/
8/Pz/+zs7P/39/f///////b29v/z8/P/9PT0//j4+P/5+fn/6+vr/0ZGRv+8vLz/z87O/0Fab/8H
b7//BJL//wSR//8Ekf//BJH//wWQ+/8Fjvj/BY74/wWO+P8FkPv/DWy2/xAxS/8QMEr/DSxE/wlI
ev8Gjvf/BJH//wSR//8BkP//MqT8/+rz+f/6+vn/+fn5//n5+f/5+fn/+fn5//r6+v/x8fH/cXFx
/xgYGP+Pj4//6urq//b29v/z8/P/9/f3//n5+f/29vb/8/Pz//b29v/s7Oz/7u7u//z8/P/+/v7/
5+fn/0VFRf+7u7v//P7//1aYyv8JRnX/C3LB/waR/f8GkPr/B5H8/xBio/8RN1X/EDhX/w83Vv8O
Nlb/W3KD/7e1tP+ysK7/fXp4/wwVG/8KToL/BY/6/wSR//8BkP//MaT8/+fy+f/6+fn/+fn5//n5
+f/5+fn/+fn5//n5+f/29vb/vLy8/zc3N//BwcH///////Ly8v/s7Oz/+Pj4///////19fX/7Ozs
//X19f/39/f/9/f3//T09P/19fX/7e3t/0hISP+7u7v/9/z9/1Gx+f8DNFn/CSE1/wo1Vv8KNFX/
CDJU/2R1g/+xrqz/sK6t/7Kwrv+wrqz/zcvK//n5+f/8/Pz/5eXl/358ev8LMlD/B472/wSR//8B
kP//MaT8/+Xy+v/6+vn/+fn5//n5+f/5+fn/+fn5//n5+f/6+vr/8PDw/0dHR/+4uLj/9/f3//b2
9v/39/f/9fX1//T09P/29vb/9/f3//b29v///////f39/+/v7//u7u7/8fHx/0pKSv+2ubv/iMr7
/x9Zhf8IFR//bmxq/6Kgnv+mpKL/qaem/9DPz//y8vL/+Pj4///////5+fn/7u7u//Pz8///////
/v7+/66urf8NFx//Ckp9/waO+P8Dkf//EZf+/2y++//r8/n/+fn5//n5+f/5+fn/+fn5//n5+f/y
8vL/eXl5/xkZGf9AQED/VVVV/8vLy///////8/Pz/+zs7P/39/f///////b29v/19fX/9fX1//b2
9v/39/f/7Ozs/0lJSf+2uLn/U3eS/wMSHv9ycG//4ODg//z8/P/6+vr/+vr6//j4+P/29vb/9vb2
//X19f/29vb/9/f3//b29v/19fX/9/f3/+Li4v+Af37/Dhcf/wxPg/8Fjvf/ApD//xGW/v9Xs/r/
c8D5/+n1/P/9/fz/+vr6//Dw8P+Li4v/l5eX/6enp/+hoaH/MzMz/0pKSv/MzMz/+fn5//f39//2
9vb/9fX1//b29v/s7Oz/7u7u//z8/P/+/v7/7e3t/6ysrP9ycnL/IyIi/25tbf/Y2Nj/+/v7////
///09PT/7Ozs//b29v//////9vb2/+zs7P/09PT///////j4+P/s7Oz/9fX1/9XV1f9WVFP/Cx4t
/wpmrf8Fj/r/BJH//wOR//8Aj///DJX+/1m3/P93xPv/6PT8/+zr6v9JSUn/yMjI///////7+/v/
vLy8/52dnf99fX3/xsbG///////19fX/7Ozs//X19f/29vb/9vb2//b29v/29vb/9vb2//X19f+p
qan/kJCQ/9vb2//5+fn/9vb2//b29v/29vb/9vb2//b29v/29vb/9vb2//b29v/29vb/9vb2//b2
9v/29vb/+vr6/7Curv8MITL/C2et/wSR/P8Ekf//BJH//wSR//8Ekf//BJH//wCP//8Mk/7/XLf8
/3G89P+cq7X/5+bl//r6+v/5+fn//Pz8//z8/P+6urr/d3d3/8DAwP/4+Pj/9vb2//b29v//////
/f39/+/v7//u7u7/+/v7//7+/v/19fX/8fHx//v7+///////8/Pz/+zs7P/39/f///////X19f/s
7Oz/9fX1///////39/f/7Ozs//Pz8////////Pz8/6uqqv8MHCn/DVqX/waP+v8Ekf//BJH//wSR
//8Ekf//BJH//wSR//8Ekf//AI///wmT/v9rvv3/4fD6//v6+f/5+fn/+fn5//n5+f/8/Pz/YGBg
/5OTk//7+/v///////b29v/29vb/9vb2//X19f/19fX/9vb2//b29v/19fX/9fX1//b29v/29vb/
9vb2//X19f/29vb/9vb2//b29v/19fX/9vb2//b29v/29vb/9fX1//b29v/29vb/+vr6/7Cvrv8N
IDD/DGCj/wWP+/8Ekf//BJH//wSR//8Ekf//BJH//wSR//8Ekf//BJH//wWT//8Klf7/Y7n7/9zt
+f/7+vn/+fn5//j4+P+pqan/LS0t/5ubm//6+vr/9vb2//b29v/s7Oz/7u7u//z8/P/+/v7/8PDw
/+3t7f/6+vr///////Ly8v/s7Oz/+Pj4///////09PT/7Ozs//b29v//////9vb2/+zs7P/19fX/
//////j4+P/s7Oz/9vb2/7Wzsv8NNlT/BZD4/wSU//8Ek///BJH//wSR//8Ekf//BJH//wSR//8E
kf//BYz0/wtUkP8LTYP/Dobj/7/h+////fz//f39//v7+/9dXV3/AAAA/6Ojo//5+fn/7Ozs//X1
9f/09PT/9PT0//f39//39/f/9fX1//T09P/39/f/9/f3//X19f/09PT/9vb2//f39//29vb/9PT0
//b29v/39/f/9vb2//T09P/29vb/9/f3//b29v/29vb/19fX/2ZkYv8JM1P/B3/a/whRif8JX6H/
BpD4/wSR//8Ekf//BJH//wSR//8Ekv//B4fr/wUXKP8ECQ//EHrK/7zg+v+urKr/h4eH/4aGhv8y
MjL/AAAA/5+fn//6+vr/9PT0//b29v///////f39//Dw8P/u7u7/+/v7//7+/v/x8fH/7e3t//n5
+f//////8/Pz/+zs7P/39/f///////X19f/s7Oz/9fX1///////39/f/7Ozs//Pz8///////srKy
/wQCAf8ELk//JovX/3h7fv9odoH/FWSi/waP9v8Ekv//BJH//wSR//8Ekf//Boz0/w1Vjv8NTYH/
EYfi/7jb9P9RT07/UlJS/3p6ev97e3v/d3d3/8DAwP/5+fn///////b29v/4+Pj/+Pj4//T09P/0
9PT/9/f3//j4+P/19fX/9PT0//f39//4+Pj/9fX1//Pz8//29vb/+Pj4//b29v/z8/P/9vb2//j4
+P/39/f/8/Pz//X19f/8/Pz/rq2s/wgZJv8IR3n/SX+r//b5+//Ozcz/FyIs/wpZmP8Fjfb/BJH/
/wSR//8Ekf//BJH//wWT//8Ckf//DJT+/7rb9P9XVVP/s7Oz//39/f/7+/v/+Pj4//T09P/29vb/
+Pj4//b29v/t7e3/7u7u//z8/P/+/v7/8PDw/+3t7f/6+vr//v7+//Ly8v/t7e3/+Pj4///////0
9PT/7Ozs//b29v//////9vb2/+zs7P/19fX///////j4+P/y8vL/qael/wczVf8jhtL/kZWY//b2
9v/i4eH/amdk/wwjNf8Ghur/BJL//wSR//8Ekf//AI///wmS/v9XtPv/cL75/5Cjsv+Ih4b/2NjY
//T09P/t7e3/+Pj4///////19fX/7Ozs//X19f/y8vL/8/Pz//j4+P/5+fn/9PT0//Ly8v/4+Pj/
+fn5//X19f/y8vL/9/f3//n5+f/19fX/8vLy//b29v/5+fn/9vb2//Ly8v/29vb/+fn5//j4+P/Y
2Nj/amlo/yI8UP+QyfX/9fj6//r6+f/p9Pz/irzi/xRViv8FjPL/BJT//wST//8Pl///Wrb9/3XB
+v/e7PX/sK+t/zAwMP++vr7//f39//T09P/y8vL/9/f3//r6+v/29vb/8vLy//b29v/+/v7//f39
//Dw8P/u7u7/+/v7//7+/v/y8vL/7e3t//n5+f/+/v7/9PT0/+3t7f/39/f///////X19f/t7e3/
9fX1///////39/f/7e3t//f39/+srKz/JSUl/42Njf/39/f/+fn5//z7+v/L2+j/HHa9/weI6f8J
ZK3/DGGm/wtfpP8dZqL/j52o/6fP6/+dzvH/LThA/1FQT//Ozs7/7+/v//n5+f/+/v7/8/Pz/+3t
7f/39/f///////b29v/6+vr/+fn5//Pz8//y8vL/+fn5//r6+v/09PT/8vLy//j4+P/6+vr/9fX1
//Hx8f/39/f/+vr6//X19f/x8fH/9vb2//r6+v/39/f/8fHx//j4+P+np6f/Xl5e//f39//5+fn/
+fn5//z8/P/My8v/GCc1/xddk/9LVFz/DxQZ/woyU/8LOV7/DUJr/wuD3/8Nbbb/ESMy/8PCwf/3
9/f/8fHx//j4+P/6+vr/9PT0//Hx8f/39/f/+vr6//b29v/t7e3/7+/v//v7+//9/f3/8fHx/+7u
7v/6+vr//v7+//Ly8v/t7e3/+Pj4//7+/v/09PT/7e3t//b29v/+/v7/9vb2/+3t7f/19fX//v7+
//v7+/+goKD/Xl5e//j4+P/7+/v/+vr6//39/f/Nzc3/ICEh/2doaf/DwsL/ITA8/weA3/8Fkv7/
BZH9/wWJ7v8LKkH/RkVE/8vLy//8/Pz//v7+//Pz8//t7e3/+Pj4//7+/v/19fX/7e3t//X19f/w
8PD/8vLy//r6+v/7+/v/8/Pz//Hx8f/5+fn/+/v7//T09P/w8PD/9/f3//v7+//19fX/8PDw//b2
9v/7+/v/9vb2//Dw8P/19fX/+/v7//v7+/+hoaH/XV1d//v7+//+/v7//////+/v7/+mpqb/cXFx
/+Xk5P/T0tL/ICoy/wpjqf8Fjvf/BJL//wSI7f8XNEn/wsC///Pz8//5+fn/+/v7//T09P/w8PD/
+Pj4//v7+//19fX/8PDw//b29v/9/f3//Pz8//Hx8f/v7+//+/v7//39/f/y8vL/7u7u//n5+f/+
/v7/9PT0/+7u7v/39/f//v7+//X19f/u7u7/9vb2//7+/v/39/f/7u7u//f39//CwsL/eHh4/9LS
0v//////8vLy/6ioqP98fHz/5eXl//7+/v/m5ub/VVRU/wweLv8GgeD/BJP//wSI7f8YNEr/zMrJ
///////y8vL/7u7u//n5+f/9/f3/8/Pz/+7u7v/39/f//v7+//b29v/8/Pz/+vr6//Ly8v/x8fH/
+fn5//v7+//z8/P/8PDw//j4+P/8/Pz/9PT0//Dw8P/39/f//Pz8//X19f/v7+//9vb2//z8/P/3
9/f/8PDw//T09P/8/Pz/vb29/3Fxcf/CwsL/pKSk/3R0dP/k5OT/8vLy//v7+//7+/v/0dDP/x4v
PP8EgN7/BJP//wSI7f8YNEr/ysnH//7+/v/z8/P/8PDw//j4+P/8/Pz/9PT0//Dw8P/39/f//Pz8
//b29v/u7u7/8PDw//v7+//8/Pz/8fHx/+/v7//5+fn//f39//Pz8//u7u7/+Pj4//39/f/09PT/
7u7u//b29v/9/f3/9vb2/+7u7v/19fX//f39//f39//v7+//8/Pz/8DAwP9JSUn/bW1t/+Xl5f/9
/f3/+vr6/+/v7//y8vL/5uXl/1BcZv8Tcr3/BY75/wSI7v8YNEr/wsG///Ly8v/6+vr//f39//Pz
8//u7u7/+Pj4//39/f/19fX/7u7u//X19f/v7+//8PDw//r6+v/7+/v/8vLy/+/v7//5+fn//Pz8
//Pz8//v7+//+Pj4//z8/P/19fX/7+/v//b29v/8/Pz/9vb2/+/v7//19fX//Pz8//f39//v7+//
9PT0//n5+f/t7e3/5+fn//Ly8v/8/Pz/+vr6//Dw8P/x8fH/+/v7/9nZ2f8qPk3/BH/b/wSL8P8X
NEn/wsC///Ly8v/5+fn//Pz8//Pz8//v7+//+Pj4//z8/P/19fX/7+/v//X19f/8/Pz/+/v7//Hx
8f/w8PD/+vr6//z8/P/y8vL/7+/v//j4+P/9/f3/9PT0/+7u7v/39/f//f39//X19f/u7u7/9fX1
//39/f/39/f/7u7u//T09P/9/f3/+Pj4/+/v7//z8/P//f39//n5+f/v7+//8fHx//z8/P/7+/v/
8fHx/93c2/9KVV7/Dm64/wt0xv81TF3/09HQ///////y8vL/7+/v//n5+f/8/Pz/8/Pz/+7u7v/3
9/f//f39//b29v/9/f3/+/v7//Hx8f/w8PD/+vr6//z8/P/y8vL/7+/v//n5+f/9/f3/9PT0/+/v
7//39/f//f39//X19f/u7u7/9vb2//39/f/39/f/7u7u//T09P/9/f3/+Pj4/+/v7//y8vL//Pz8
//n5+f/v7+//8fHx//z8/P/7+/v/8PDw//Dw8P/c3d3/UFdd/z1FTP/CxMb/+Pj4//z8/P/y8vL/
7+/v//n5+f/9/f3/9PT0/+7u7v/39/f//f39//b29v/v7+//8fHx//r6+v/7+/v/8vLy//Dw8P/5
+fn//Pz8//Pz8//v7+//+Pj4//z8/P/19fX/7+/v//b29v/8/Pz/9vb2/+/v7//19fX//Pz8//f3
9//v7+//9PT0//z8/P/4+Pj/8PDw//Ly8v/7+/v/+vr6//Dw8P/y8vL/+/v7//v7+//x8fD/4eDg
/+no6P/5+fn/8/Pz//Dw8P/5+fn//Pz8//Pz8//v7+//+Pj4//z8/P/19fX/7+/v//b29v/s7Oz/
7u7u//z8/P/+/v7/8PDw/+3t7f/6+vr///////Ly8v/s7Oz/+Pj4///////09PT/7Ozs//b29v//
////9vb2/+zs7P/09PT///////j4+P/s7Oz/8vLy//7+/v/5+fn/7e3t//Dw8P/+/v7/+/v7/+7u
7v/v7+///f39//39/f/v7+//7+/v//z8/P/+/v7/8PDw/+3t7f/6+vr//v7+//Ly8v/s7Oz/+Pj4
///////19fX/7Ozs//X19f8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAoAAAAnAAAADgBAAABAAgAAAAAABBfAAAAAAAAAAAAAAABAAAAAQAA7OzsAPLy8gD///8A9fX1
AP7+/gD7+/sA+fn5AO3t7QDw8PAAycnJAOHh4QAAAAAAqampAK6urgBoaGgAHUJiACSV8AAlT3IA
X19fABREagADlf8ABJH/AAKS/wAUS3YA0tLSAF9ufQAPL0oAGzVOACFdkAAeHh4AFXTBABiX/gAz
MzMABAQEACkpKQCTk5MAi4uLAIKCggC9vb0AS0tLABQrQgASJDoAFXvMACCY9gASEhIAFV2YAIaT
ngCcnJwAeXl5ACJjmgALDh8AACxOABI6XQAACS0AICw6ADw8PABHo+oAQ6TvAD2HwACs1vYAc7v3
APX8/ADv//8AkMzyAACN/wBnuO4AAIz4AFGv8wBImNgA5fT7AMTj9wDR8PoADhkqADij9wC83PMA
EojnAIC/7wAVh+EAYZrNABaJ5QBRUVEAK37CADlEUwBAZYYAJIPSACBUgQAecLYAuef4ALjd9gB4
wPAALCwsAJ2tuwDj/P8AI3O1AFVzjwAiaqYAgp+4AAAzXgDP2+IAptz3AAAjQgCNt9UANk1kAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQEBAQEBAUABwcHBwAGAgQE
BAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQF
AAcHBwcAAwIEBAQEAggHBwcHBwcCBAQEBAQGAAcHBwcABgQEBAQEAgcHBwcHBwECBAQEBAIDAAcH
BwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwICAgICAgUAAAAAAAAGAgICAgICCAAAAAAABwICAgIC
AgYAAAAAAAAFAgICAgICAAAAAAAAAQICAgICAgMAAAAAAAAEAgICAgIFAAAAAAAAAwICAgICAggA
AAAAAAcCAgICAgIGAAAAAAAABQICAgICAgAAAAAAAAECAgICAgIDAAAAAAAABAICAgICBAAAAAAA
AAMCAgICAgIBAAMBAQEBAQMGBgYGBgYDAQEBAQEBBgYGBgYGBgEBAQEBAQMGBgYGBgYDAQEBAQED
BgYGBgYGBgEBAQEBAQYGBgYGBgYDAQEBAQEDBgYGBgYGAwEBAQEBAQYGBgYGBgYBAQEBAQEDBgYG
BgYGAwEBAQEBAQYGBgYGBgYBAQEBAQEGBgYGBgYGAwEBAQEBAwYGBgYGBgYBAQEBAQEGBgcAAAAA
AAECBAQEBAIDAAAAAAAABAIEBAQCBAAAAAAAAAMCBAQEBAIBAAAAAAAAAgQEBAQCBQAAAAAAAAYC
BAQEBAIHAAAAAAAIAgQEBAQCAwAAAAAAAAUCBAQEAgQAAAAAAAADAgQEBAQCAQAAAAAAAAIEBAQE
AgUAAAAAAAAGAgQEBAQCBwAAAAAACAIEBAQEAgYAAAAAAAAFAgcHBwcHBwECBAQEBAIDAAcHBwcA
AgICAgICAgEDAwMDAQUCAgIEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQE
AgICBAEDAwMDAQICAgICAgIBAwMDAwEFAgICAgICBQMDAwMDAQICAgIEBAUABwcHBwAGAgQEBAQC
CAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcBIyUlJSUlJTAwMDAwMDAl
JSUCBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCIyUlJTAwMDAwMCUlJSUl
JSUwMDAwMDAwJSUlJSUlMDAwMDAwMCUlMBgCBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYA
BwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcDWgsLCwsLCwsLCwsLCwsLCwsCBAIBBwcHBwcHAgQE
BAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCWgsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsL
CwsLCwsLCwsLCyYCBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwEC
BAQEBAIDAAcHCAgGIAsLCwsLCwsLCwsLCwsLCywCBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQE
BAIHBwcHBwcIAgQCIAsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCyYCAgQA
BwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAAAAAAAAAECAgICAgIDAAcKJgkJZho0
UhISEhISEhISEjcLCywCAgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAAAAAAIAgICIAsL
NxISEhISEhISEhISEhISEhIdCwsgEhISEhISEhISEhISEhISEgwYGBgHAAAAAAAGAgICAgICBwAA
AAAACAICAgICAgYAAAAAAAAFAgQEBAQEBAUHBwcHBwcGBAIKCwsLTR8WPwICAgICAgICAg0LCywD
BwcFBAQEBAQCBwcHBwcHAQIEBAQEAgMHBwcHBwcEBAQEBAQFBwcDIAsLLwICAgICAgICAgICAgIC
AgISCwslAgICAgICAgICAgICAgICAjALC1ACBAQEBAIDBwcHBwcHBAQEBAQEBQcHBwcHBwMCBAQE
BAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTRZAPwUGBgYGBgYGBA0LCywDBwAFAgQEBAQCAAcHBwcH
AQIEBAQEAgMABwcHBwAEBAQEBAQFAAcDIAsLLwIGBgYGBgYGBgYGBgYGBgISCwslAgYGBgYGBgYG
BgYGBgYGAjALCxICBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcH
BwAGAgIKCwsLTRZATD4+PgYGBgYGBA0LCywDBwACAgICAgICAQMDAwMDBQICAgIEAgMABwcHBwAE
BAQEBAQFAAcDIAsLLwIGBgYGBgYGBgUCAgICAgISCwslPj4+BgYGBgYGBgYGBgYGAjALCxICBAQE
BAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTRYVHxAQ
OD0GBgYGBA0LCywDBwMSCywsLCwsLCwsLCwsLCwsCwQCAgMABwcHBwAEBAQEBAQFAAcDIAsLLwIG
BgYGBgYGBAwLLCwsLCwLCwsRKxBJPQYGBgYGBgYGBgYGAjALCxICBAQEBAIDAAcHBwcABAQEBAQE
BQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVED0GBgYGBA0LCywDBwMS
CwsLCwsLCwsLCwsLCwsLCwICAgMABwcHBwAEBAQEBAQFAAcDIAsLLwIGBgYGBgYGAgwLCwsLCwsL
CwsXFBVCPQYGBgYGBgYGBgYGAjALCxICBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIB
BwIEBAQEAgUABwcHBwAGAgIKCwsLTRYVFRUVST0FBAICAg0LCywDBwMSCyELCwsLCwsLCwsLCyEh
CwICAgMABwcHBwAEBAQEBAIFAAcDIAsLLwIGBgUFBQUFAgwLCwsLCwsLCwsXFBUfPQQFBQUFBAIC
AgICAiULCxICBAQEBAIDAAcHBwcABAQEBAQEBAAHBwcHAAMCBAQEBAIBAAUFBQUFBQYIAQEBAQgG
BQQKCwsLTRYVFRUVH1lZWS4kJBILCywGAQYSCwtQDQ0NDQ0NDQ0NJAshCwUFBQMBAQEBAQgFBQUF
BQUGCAEGIAsLLwIGRVlZWVlZWWUNDQ0NDQ03CwsXFBUWWVlZWVlZZSQkJCQkJCcLCxICBQUFBQUD
AQEBAQEIBQUFBQUFBQgBAQEBAQMFBQUFBQUBAQAAAAAAAAECAgICAgIDAAgYCwsLTRYVFRUVFUBA
FmQLCwsLCywCAgISCwslAgQEBAQEBAQCCQshCwcHAAYCAgICAgIHAAAAAAAIAgICIAsLLwIGR0BA
QEBAQEwCBAQEBAISCwsXFBUVQEBAQEAVHgsLCwsLCwsLCxIDAAAAAAAGAgICAgICBwAAAAAACAIC
AgICAgYAAAAAAAAFAgcHBwcHBwECBAQEBAIDAAgYCwsLTRYVFRUVFRUVFBoLCwsLCwsCBAISCwsw
AgYGBQUFBQUCCQshCwcHAAYEBAQEBAIHBwcHBwcIAgQCIAsLLwIFRUIVFRUVQEwEBQUFBQISCwsX
FBUVFRUVFRUWHgsLCwsLCwsLCxIDBwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcH
BwcHBwECBAQEBAIDAAgYCwsLTRYVFRUVFRUVFBoLC1oSUBICBAISCwswAgYGRldXYhgYDAshCwcH
AAYEBAQEBAIHBwcHBwcIAgQCIAsLLldGY0AVFRUVQEFGWEYYGApQCwsXFBUVFRUVFRUWKigbGwsL
CzdQUCUBBwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgY
CwsLTRYVFRUVFRUVFBoLCyMCAgIEBAISCwswAgY9QkIWYQsLCyEhCwcHAAYEBAQEBAIHBwcHBwcI
AgQCIAsLLRVCQhUVFRUVFRVCQksLCwsLCwsXFBUVFRUVFRUVFh8fKwsLCyYCAgIABwcHBwAGAgQE
BAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLTRYVFRUVFRUVFBoL
CyMCBAQEBAISCwswAgY9QhUUEwshISEhCwcHAAYEBAQEBAIHBwcHBwcIAgQCIAsLLRQVFRUVFhUV
FRUVFksLCwsLCwsXFBUVFRUVFRUVFRUVHwsLCyYCBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQE
AgYABwcHBwAFBAAAAAAAAAECAgICAgIDAAgYCwsLTRYVFRUVFRUVFBoLCyMCAgICAgIOCwslPT5c
QhUUEwshCwsLCwcHAAYCAgICAgIHAAABAwMGAgICNwsLLRQVFRUVFRUVFRUVFksLCwsLCwtVHx8f
Hx8fFhUVFRUVHwsLCyYCAgUAAAAAAAAGAgICAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgYGBgYG
BgYDAwMDAwMDBgYKCwsLTRYVFRUVFRUVFBoLCyxaIiIiIlosCwsRSUlJFRUUEwsLDgEAAAYGBgMD
AwMDAwMGBgQjLCIiIiJaIQsLLRQVFRUVFRUVFhUVFRVNTRAbCwssSEhISEgsKhYVFRUVHwsLCw0F
AwMGBgYGBgYDAwMDAwMDBgYGBgYGBgMDAwMDAwMGBgYGBgYDAwICAgICAgUAAAAAAAAGAgIKCwsL
TRYVFRUVFRUVFBoLCwsLCwsLCwsLCwsXFBUVFRUUEwsLMAICAgICAgMAAAAAAAAEAgIjCwsLCwsL
CwsLLRQVFRUVFRYVFRUVFRUWFhQ0CwsLCwsLCwsLHhQVFRYVHwsLCw0BAAECAgICAgIDAAAAAAAA
BAICAgICBAAAAAAAAAMCAgICAgIBAAQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVFRUVFCgLCwsL
CwsLCwsLCwsXFBQUFBQUEwsLMAICAgICAgUBAQEBAQECAgIjCwsLCwsLCwsLLRQUFBUVFRUVFRUV
FRUVFRQzCwsLCwsLCwsLHhQUFBQUHwsLCw0GAQMCBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMC
BAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVFRUVFlYxMTExMRwLCwsLCwsoHBwcHBwc
KQsLNy8jIyMjIyMkJCQkJCQjIy9eLTExMTExMTExHBxVMRQVFRUVFRUVFRUVFRVgDAwMDAwMCwsL
DxwcHBwcVQsLCw4jJAwCBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUA
BwcHBwAGAgIKCwsLTRYVFRUVFRUVFRQUFBQUFCsLCwsLCwsLCwsLCwsLCyEhCwsLCwsLCwsLCwsL
CwsLCwtWFBQUFBQUFBQULQsLSB8VFRUVFRUVFRUVFUBGAgICAgICCwsLCwsLCwsLCwsLCwsLCxIC
BAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTxYW
FhUVFRUVFRUVFRUVFksLCwsLCwsLCwsLCwsLISEhIQsLCwsLCwsLCwsLCwsLCwtfFBUVFRUVFRUU
LQsLKRQWFhUVFRUVFRUVFUBGBQYGBgUFCwsLCwsLCwsLCwsLCwsLCxICAgIEBAIDAAcHBwcABAQE
BAQEBQAHBwcHAAMCBAQEBAIBBwICAgICAgUAAAAAAAAGAgIKCwsLXVRUTxYVFRUVFRUVFRUVFh8p
KCgoKCgoKCgoCwsLISEhIQsLCygoKCgoKCgoKCgoKClWFBUVFRUVFRUULQsLSFRUVEIVFRUVFRUV
FUBGBQYGBgUFICcnJycnJycnJycnJx0LCxIACgoEAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgIC
AgIBAAgICAgICAEEBAQEBAQDCAEYCwsLCwsLLRQVFRUVFRUVFRUVFRYfHx8fHx8fHx8rCwsLCwsL
CwsLCysfHx8fHx8fHx8fHx8WFRUVFRUVFRUULQsLCwsLC00WFRUVFRUVFUBGBQYGBgYFAgICAgIC
AgICAgICAiULCwsLCwsACAcGBAQEBAQEAQgICAgIAQQEBAQEBAYHCAgICAcFBAcHBwcHAAECBAQE
BAIDAAgYCwsLCwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUfCwsLCwsLCwsLCx8VFRUVFRUVFRUV
FRUVFRUVFRUVFRUULQsLCwsLC00WFRUVFRUVFUBGBQYGBgYGBgYGBgYGBgYGBgYGAjALCwsLCwsK
BwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLCwsLLRQV
FRUVFRUVFRUVFRUVFRUVFRUVFRUfCwsLCwsLCwsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUULQsL
CwsLC00WFRUVFRUVFUBYPT49BgYGBgYGBgYGBgYGBgYGAjALCwsLCwsHAwEFAgQEBAQCCAcHBwcH
CAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcAGBgKIAsLLRQVFRUVFRUVFRUVFRUVFRUV
FRUVFRUfCwsLX1RUXwsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUWS1RUUQsLC00WFRUVFRUVFRVJ
OUk/BQYGBgYGBgYGBgYGBgYGBQAKCiYLCwsgICImAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAF
BAcHBwcHBwECBAQEBAIDAAcHCAgDNwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUfCwsLHhQUHgsL
Cx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRYWTwsLC00WFRUVFRUVFRUVFUA8BAYGBgYGBgYGBgYG
BgYGBgUFBBgLCwsLCwsNAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHAAECBAQEBAID
AAcHBwcDNwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUfCwsLHhYUHgsLCx8VFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUWTQsLC00WFRUVFRUVFRUVFUA8BQYGBgYGBgYGBgYGBgYGBgYGBAkLCwsLCwsN
AgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAgICAgICAEEBQUFBQQDCAgICAgGNwsLLRQVFRUV
FRUVFRUVFRUVFRUVFRUVFRUUHBwcTRYUHgsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUWTQsL
C00WFRUVFRUVFRUVFUA8BQYGBgYGBgYGBgYGBgYGBgYGBQojLy8hCwsNAgUFBQUEAQgICAgIAQQF
BQUFBAYICAgICAgFBAICAgICAgUAAAAAAAAGAgICAgICNwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFBQUFhUUHgsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUWTQsLC00WFRUVFRUVFRUVFUA8
BAYGBgYGBgYGBgYGBgYGBgYGBgUCAgIsCwsMAQAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAQE
BAQEBAUABwcHBwAGAgQEAgICNwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUUHgsLCx8V
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUWTQsLC00WFRUVFRUVFRUVFUA8BAUFBgYGBgYGBgYGBgYG
BgYGBgYGBgIsCwsMAwgIBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQF
AAAIUilILRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUUHgsLCx8VFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUWSzIpMk0WFRUVFRUVFRUVFUBDR0dHBQYGBgYGBgYGBgYGBgYGBgYGBgIsCwsjCgoK
BwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTR8fHxUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUUHgsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFR8fHxYV
FRUVFRUVFRUVFRUVQkJLPQYGBgYGBgYGBgYGBgYGBgYGBgIsCwsLCws3AwcABAQEBAQEBQAHBwcH
AAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUUHgsLCx8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUf
PQYGBgYGBgYGBgYGBgYGBgYGBgIsCwsLCwsnAwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwICAgIC
AgUAAAAAAAAGAgIKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUWHgsLCx8VFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUUPj09BQYGBgYGBgYGBgYG
BgYGBgILCwsLCwsnAwAABAICAgICBAAAAAAAAAMCAgICAgIBAAYGBgYGBgYDAwMDAwMDBgYKCwsL
TRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVH1RUVBYVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUWOTk5RgUGBgYGBgYGBgYGBgYGBgUKCgowCwsnBAMD
BgYGBgYGBgMDAwMDAwMGBgYGBgYDAwAAAAAAAAECAgICAgIDAAgYCwsLTRYVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRYWFhUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYGBgYFBQIkCwtQAgICBwAAAAAACAICAgICAgYA
AAAAAAAFAgcHBwcHBwECBAQEBAIDAAgYCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVA
WAUGBgYGBgYGBgYGBgYGBgYGBgIkCwsnAgICCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwEC
BAQEBAIDAAgYCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYG
BgYGBgQmJCMjDAwMCgcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLTRYV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYGBgYGBgYEAgIKCwsLCggH
BwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLTRYVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYGBgYGBgYGBgUYCwsLCgcHBwcHCAIEBAQEAgYABwcH
BwAFBAAAAAAAAAECAgICAgIDAAgYCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAWAUG
BgYGBgYGBgYGBgYGBgYGBgYGBgUYCwsLCgcAAAAACAICAgICAgYAAAAAAAAFAgUFBQUFBQYIAQEB
AQgGBQQKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYGBgYG
BgYGBgUYCwsLAAQFBQUFBQgBAQEBCAMFBQUFBQUBCAIEBAQEAgUABwcHBwAGAgIKCwsLTRYVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAWAUGBgYGBgYGBgYGBgYGBgYGBgYGBgUYCwsLBwIEBAQE
BAAHBwcHAAMCBAQEBAIBAAQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVQkJCWAUGBgYGBgYGBgYGBgYGBgYGBgYGBgUYCwsLAAIEBAQEBQAHBwcHAAMCBAQEBAIB
BwQEBAQEBAUABwcHBwAGAgIKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUUV1dYRQYGBgYG
BgYGBgYGBgYGBgYGBgYGBgUYCwsLAAIEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAG
AgIKCwsLTRYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUfPQUFBgYGBgYGBgYGBgYGBgYGBgYGBgYG
BgUYCwsLAAIEBAQEBQAHBwcHAAMCBAQEBAIBBwIEBAQEBAUABwcHBwAGAgIKCwsLTxQUFhUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVQEBCPQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYFBAIKCwsLAAIEBAQEBQAH
BwcHAAMCBAQEBAIBAAQEBAQEBAUHBwcHBwcGBAIKCwsLHF9fKhYVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVJ
WVlZPQYGBgYGBgYGBgYGBgYGBgYGBgYGBgUYDQ0vCwsLAAIEBAQEBQcHBwcHBwMEBAQEBAQBBwAA
AAAAAAECAgICAgIDAAgYCwsLCwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUA8BAUFBgYGBgYGBgYGBgYG
BgYGBgYGBgYGBgIlCwsLCwsLCgcAAAAACAICAgICAgYAAAAAAAAFAgcHBwcHBwECBAQEBAIDAAgY
CwsLCwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUA8BAYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIkCwsL
CwsLCggHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLCwsLLRQVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUrECtMBAYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIkCwsLLCELCggHBwcHCAIEBAQE
AgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLCwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUBXPj49BgYG
BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIkCwtQAgICCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcH
BwECBAQEBAIDAAgYCwsLCwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUBGBQYGBgYGBgYGBgYGBgYGBgYGBgYG
BgYGBgYGBgIkCwtQAgQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcAAAAAAAECBAQEBAIDAAgYCwsL
CwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFUBGBQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIkCwtQAgIC
CAAAAAAACAIEBAQEAgYAAAAAAAAFAgMDAwMDAwMGBgYGBgYDAwMHCQkYIAsLLRQVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFUBGBQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIkCwtQAgYGAwMDAwMDAwYGBgYGBgYD
AwMDAwMGBgICAgICAgUAAAAAAAAGAgICAgICNwsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUBGBQYGBgYGBgYG
BgYGBgYGBgYGBgYGBgYGBgYGBgIkCwsnAwAABAICAgICBAAAAAAAAAMCAgICAgIBAAQEBAQEBAUA
BwcHBwAGAgQCAgICIAsLLRQUFhUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAQEBGBQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYG
BgYEBAIkCwsnAwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIDJiYmJTAl
Xl1fVhYVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFR9BQUFFBQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgUmJiYOCwsnAwcABAQE
BAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLAAICLwsLMh8VFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFSs9
BAUFBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgILCwsLCwsnAwcABAQEBAQEBQAHBwcHAAMCBAQE
BAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLCgUCLwsLKRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRYVFhUVFRUVFRUVFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYG
BgYGBgYGBgYGBgYFBQIsCwsLCwsnAwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwICAgICAgUAAAAA
AAAGAgIKCwsLCgUCLwsLMhAQEB8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFR8QEBAQ
EBAQEBAQEBAQFhUVFRUVFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgUFBQIs
CwsLCws3AQAABAICAgICBAAAAAAAAAMCAgICAgIBAAEBAQEBAQMFBQUFBQUDAQMYCwsLCgUGBAIC
BwsLCyoWFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFioLCwsLCwsLCwsLCwsLTxYVFRUV
FRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBQkLCwsLCwsNAgICBQUFAQEBAQEB
AQUFBQUFBQYBAQEBAQEGBQcABwcHAAECBAQEBAIDAAgYCwsLCgUGBgYFAAsLCyoWFRUWFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFioLCwsLCwsLCwsLCwsLTRYVFRUVFRUVFRUVFRUVFSs9BgYG
BgYGBgYGBgYGBgYGBgYGBgYGBgYGBQkLCwsLCwsNAgICBAQCBwAHBwcACAIEBAQEAgYABwcHBwAF
AgcHBwcHBwECBAQEBAIDAAgYCwsLCgUGBgYFAAsLCyoUFBQVFRUVFRUVFRUVFRUVFBQUFBQUFBQU
FBQUFBQUFCoLCwsLCwsLCwsLCwsLTRQUFBUVFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYG
BgYGBgYGBQkLCwsLCwsNAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAID
AAgYCwsLCgUGBgYFRR5dUREPD1YUFRUVFRUVFRUVFRUfDw8PDw8PDw8PDw8PDw8PNBkYCQkmJiYm
JiYMCwsLGw8PVhYWFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBQAmCQksCwsN
AgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLCgUGBgYGRUAW
FBoLCxwUFRUVFRUVFRUVFRUfCwsLCwsLCwsLCwsLCwsLCxICAgIBAQEBAQEYCwsLCwsLLRQVFRUV
FRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgUEBAIsCwsNAgQEBAQCCAcHBwcHCAIE
BAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYCwsLCgUGBgYGRUIVFBoLCxwUFhYWFhYWFhYW
FhQfCwsLCwsLCwsLCwsLCwsLCxICBAIHBwcHBwgYCwsLCwsLLRQVFRUVFRUVFRUVFSs9BgYGBgYG
BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIsCwsNAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAAA
AAAAAAECAgICAgIDAAgYCwsLCgUGBgYGRUIVFBoLCw9dXV1dXV1dXV1dXV1dMDAwMDAwMA4ODg4O
DjAwMC8CAgIHAAAAAAcYDjAwHQsLLRQVFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYG
BgYGBgYGBgIsCwsNAgICAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgICAgICAgUAAAAAAAAGAgIK
CwsLCgUGBgYGRUIVFBoLCwsLCwsLCwsLCwsLCwsLBQMDAwMDBQICAgICAgUDAwEAAAACAgICAgIE
AwMFIAsLLRQVFRUVFRUVFRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgIsCwsMAQAA
AAAABAICAgICBAAAAAAAAAMCAgICAgIBAAQEBAQEBAUABwcHBwAGAgIKCwsLCgUGBgYFRUIVFBoL
CwsLCwsLCwsLCwsLCwsLAwcHBwcAAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcDIAsLLRQVFRUVFRUV
FRUVFSs9BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBQIsCwsMAQcHBwcABAQEBAQEBQAHBwcH
AAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsLCgUGPVw+RysrKxsLCwsLCwsLCwsLCwsLCwsL
AwcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcDIAsLHCsrKxUVFRUVFRUVFStcXFw9BgYGBgYG
BgYGBgYGBgYGBgYGBgYGBgUCAgIsCwsMBgMDAwMBBAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQE
BAUABwcHBwAGAgIKCwsLCgUFP0IfTQsLCwsLCyQGAQEBAQECAgICAgICBwcHBwcHAQIEBAQEAgMA
BwcHBwAEBAQEBAQFAAcDIAsLCwsLSBQVFRUVFRUVFRYfH0tGBQYGBgYGBgYGBgYGBgYGBgYGBgYG
BAkLCwsLCwsLCwsLCwsLAAIEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgIKCwsL
CgUFP0AWTwsLCwsLCyUDBwcHBwAFAgQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcD
IAsLCwsLKRQVFRYVFRUVFRUVFUBGBQYGBgYGBgYGBgYGBgYGBgYGBgYGBAkLCwsLCwsLCwsLCwsL
AAIEBAQEBQAHBwcHAAMCBAQEBAIBBwIEBAQEAgUABwcHBwAGAgIKCwsLCgUFPxYUTwsLCwsLCyUB
BwcHBwAFAgQEBAQCAAcHBwcAAQIEBAQEAgMABwcHBwAEBAQEBAIFAAcDHQsLCwsLKR8UFBYVFRUV
FRUVFUBGBAQEBAQFBgYGBgYGBgYGBgYGBgQCAhgLCwsLCwsLCwsLCwsLAQICAgQCBAAHBwcHAAMC
BAQEBAIBAAUFBQUFBQYBAQEBAQEGBQUKCwsLCgUEWxMRDwsLCy8mJhgDAQEBAQEGBQUFBQUFAQEB
AQEBAwUFBQUFBQMBAQEBAQEGBQUFBQUGAQEDJiYmMAsLLBERD0sWFRUVFRUVFRVDQUFBQUFBPQQE
BAQEBQYGBgYGBAwwMCUmJiYmJiYmJiYMCwsLDjAwJgQFBgEBAQEBAQMFBQUFBQUDAQAAAAAAAAEC
AgICAgIDAAgYCwsLCgUCLwsLCwsLCxgBCAYCAgICAgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgIC
AgIHAAAAAAAIAgICAgICLwsLCwsLCyoWFRUVFRUVFRUVQEBAQEBCPQQEBAQEBAYGBgYGAjALCxIC
BAQEBAQEBAIKCwsLCwsLIwEACAICAgICAgYAAAAAAAAFAgcHBwcHBwECBAQEBAIDAAgYCwsLCgIC
LwsLCwsLCwkIAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQEAgIC
LwsLCwsLCyoWFRUVFRUVFRUVFRUVFRUfAgICAgICBAYGBgYGAjALCxICBgYGBgYGBgUYCwsLCwsL
LwMIAQIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAgYEhISJgkJJQsLLA4OEhgIAAMCBAQE
BAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCGAkYJQsLLA8PG08WFRUVFRUV
FRUVFRUVFRUUV1dXV1dXRwUFBQYGAjALCxICBgYGBgYGBgUKEg4ODg4OIyYmCQIEBAQEAgYABwcH
BwAFBAcHBwcHBwECBAQEBAIDAAcIAwMFIgsLCwsLIAUDAwgHAAMCBAQEBAIBBwcHBwcHAgQEBAQE
BgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCHQsLCwsLKR8UFBYVFRUVFRUVFRUVFRUVFRUVQkJCQkJA
QQIEAgYGAjALCxICBgYGBgYGBgYFAgICAgICLwsLWgIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQE
BAIDAAcHBwcDNwsLCwsLWgMHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIH
BwcHBwcIAgQCIAsLCwsLKRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAQQIEAgYGAjALCxICBgYG
BgYGBgYGBgYGBgYCLwsLNwIEBAQEAgYABwcHBwAFBAAAAAAAAAECAgICAgIDAAAAAAABHQsLCwsL
LAEAAAAAAAMCAgICAgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAAAAAAIAgICIAsLCwsL
SBQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVAQz0+Pj4+PjALC1ACBgYGBgYGBgYGBgYGBgYCIwsL
IgICAgICAgYAAAAAAAAFAgYGBgYGBgYBAwMDAwEGBgYGBgYGAQEBAQEBAQYGBgYGBgMBAwMDAwEG
BgYGBgYGAQMDAwMBAwYGBgYGBgMBAwMDAwEGBgYGBgYGAQMFIAsLHBAQEBYVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVHxArKysQK1gCBAUGBgYGBgYGBgYGBgYGBgYGBgYFCgsLCxgDAQMGBgYGBgYD
AwICBAQEAgUAAAAAAAAGAgQEBAQCCAcHBwcHCAICAgQEAgYAAAAAAAAFAgQEBAQCAAAAAAAAAQIE
BAQEAgMAAAAAAAAEAgQEBAIFAAcDIAsLLRQVFRUWFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVQDsCAgQGBgYGBgYGBgYGBgYGBgYGBgUFCgsLCxgIAAMCBAQEBAIBAAQEBAQEBAUABwcHBwAG
AgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQE
BAQFAAcDIAsLLRQUFBUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVQDsCAgIGBgYGBgYG
BgYGBgYGBgYGBgYFCgsLCxgIAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIE
BAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcDIAsLKFURHBQV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUNZWT8FBgYGBgYGBgYGBgYGBgYGBgYFCgsL
CxgIAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQE
BAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcDIAsLCwsLSB8VFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRVAQEMEBgYGBgYGBgYGBgYGBgYGBgYFCgsLCxgIAAMCBAQEBAIBBwQE
BAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQE
AgMABwcHBwAEBAQEBAQFAAcDIAsLCwsLSB8VFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVQEMEBQUGBgYGBgYGBgYGBgYGBQUECgsLCxgIAAMCBAQEBAIBBwICAgICAgUAAAAAAAAGAgIC
AgICCAAAAAAABwICAgICAgYAAAAAAAAFAgICAgICAAAAAAAAAQICAgICAgMAAAAAAAACAgICAgIF
AAABIAsLKQ8bExQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUlXWFg9BgYGBgYG
BgYGBgYFChgYJgsLCxgIAAMCAgICAgIBAAcHBwcHBwECBAQEBAQDBwcHBwcHBQQEBAQEBAcHBwcH
BwMCBAQEBAIBBwcHBwcHAgQEBAQEBQcHBwcHBwYEBAQEBAIIBwcHBwcBAgQCIAsLLR8fFBUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRVCQkJFBgYGBgYGBgYGBgYCIwsLCwsLCwoC
BAYHBwcHBwcFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBAAcHBwcA
AgQEBAQEBQAHBwcHAAYCBAQEBAIHBwcHBwcIAgQCIAsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFUJFBgYGBgYGBgYGBgYCLwsLCwsLCwoCAgYABwcHBwAFBAcHBwcH
BwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYE
BAQEBAIHBwcHBwcIAgQCIAsLLRQVFRUWFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFh8rKysr
Kx8VFUJFBgYGBgYGBgYGBgYCLwsLCwsLCwoCAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcA
BQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQC
IAsLLRQVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFCEyMjIyIRMUFUJFBgYGBgYGBgYG
BgYCLwsLCwsLCwoCAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMC
BAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCIAsLLRQVFRUVFRUVFRUV
FRUVFRUVFRUVFRUVFRUVFRUVFRUVHwsLCwsLCzQUFUJFBgYGBgYGBgYGBgYCLwsLCwsLCwoCAgYA
BwcHBwAFBAcHBwcHAAECBAQEBAIDAAcHBwcABAQEBAQEBAAHBwcHAAMCBAQEBAIBAAcHBwcAAgQE
BAQCBQAHBwcHAAYCBAQEBAIHBwcHBwABAgICNwsLLRQVFhQUFBQUFBQVFRUVFRUVFRUVFRUVFRUV
FRUVFRUVHwshISEhCzQUFUJFBgYEAgICAgICAgICLwsLCwsLCwoCAgYABwcHBwAFAgEBAQEBAQEF
BQUFBQUDCAEBAQEIBQUFBQUFBQgBAQEBCAMFBQUFBQUDAQEBAQEBBQUFBQUFBggBAQEBCAYFBQUF
BQUBAQEBAQEKJCQjHQsLLRQWS1VVVVVVVVYWFRUVFRUVFRUVFRUVFRUVFRUVFRUVHwshISEhCzQU
FUJFBgQmJCQkJCQkJCQjUAsLCwsLCwoEBQYIAQEBAQgGBQICAgICAgUAAAAAAAAGAgICAgICCAAA
AAAABwICAgICAgYAAAAAAAAFAgICAgICAAAAAAAAAQICAgICAgMAAAAAAAAEAgICAgIKCwsLCwsL
LRQWTQsLCwsLCxwUFRUVFRUVFRUVFRUVFRUVFRUVFRUVHwshISEhCzQUFUJFBgIkCwsLCwsLCwsL
CwsLCwsLCxgIAAMCAgICAgIBAAQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcH
BwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAIKCwsLCwsLLRQWTQsLCwsLCy0UFhYV
FRUVFhUVFRUVFRUVFRUVFRUVHwsLCwsLCzQUFUJFBgIkCwsLCwsLCwsLCwsLCwsLCxgIAAMCBAQE
BAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcH
AQIEBAQEAgMABwcHBwAEBAQEBAIKCwsLCwsLLRQWTydQUFBQUFNUVFQWFRUVFRUVFRUVFRUVFRUV
FRUWFCgbGxsbKBcUFUJFBgIkCwssUCcnUFBQUFBQUCcnNxgIAAMCBAQEBAIBBwQEBAQEBAUABwcH
BwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAE
BAQEBAIKCwsLCwsLLRQVSQICAgICAg0LCwsfFhYWFRUVFRUVFRUVFRUVFRUWFR8fHx8fHx8VFUJF
BgIkCwtQBQMBAgICAgICAgMDAwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcH
CAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAIKCwsLCwsLLRQV
ST0GBgYGAgwLCzIfFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUJFBgIkCwsnAwcABAQEBAQE
BQAHBwcHAAMCBAQEBAIBBwICAgICAgUAAAAAAAAGAgICAgICCAAAAAAABwICAgICAgYAAAAAAAAF
AgICAgICAAAAAAAAAQICAgICAgMAAAAAAAAEAgICAgIKCwsLCwsLMR8fOT0GBgYGBAwLCzIrHx8U
FRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUJFBgIkCwsnAwAABAICAgICBAAAAAAAAAMCAgICAgIB
AAMDAwMDAwMGBgYGBgYDAwMDAwMDBgYGBgYGBgMDAwMDAwMGBgYGBgYDAwMDAwMDBgYGBgYGBgMD
AwMDAwYGBgYGBgYDAwMDAwYYCwsLUU1NHDJIUgIGBgYGBAwLCwtISCwqFhUVFRUVFRUVFRUVFRUV
FRUVFRUVFRUVFUJFBgIkCwtQBAYGAwMDAwMDAwYGBgYGBgMDAwMDAwMGBgAAAAAAAAECAgICAgID
AAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAAA
AAgYCwsLTxYULQsLIAIGBgYGBAwLCwsLCwsqFhUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFUJFBgIk
CwtQAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAH
BwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwgYCwsLTRYULQsLIgIG
BgYGBAwLCwsLCwsqFhUVFRUVFRUVFRUVFRUVFRUVFUBAQEBAQEJFAgIkCwsnAgQCCAcHBwcHCAIE
BAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcH
BwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwgYCwsLTRYVTgwvDQQGBgYGBRgvDC8LCwsqFhUV
FRUVFRUVFRUVFRUVFRUVQEE/Pz8/Pz8uIyMvDAwmAgQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcH
BwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcH
AAYEBAQEBAIHBwcHBwgYCwsLTRZAPwICBAYGBgYGBgUCAgMLCwsqFhUVFRUVFRUVFRUVFRUVFRUV
QDsEBQUFBQILCwsNAgICBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcH
BwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHCAEY
CwsLSxVATAUGBgYGBgYGBgYFBQgLCwsqFhUVFRUVFRUVFRUVFRUVFRUVQDsFBgYFBQIsCwsNAgQE
BAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAAAAAAAAAECAgICAgIDAAAAAAAABAICAgICBAAAAAAA
AAMCAgICAgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAcKGBgmCwsLRDk5OwUGBgYGBgYG
BkVGR0Y1KEgqFhUVFRUVFRUVFRUVKzk5OTk5SUoFBQEKCgosCwsNAgICAgICBwAAAAAACAICAgIC
AgYAAAAAAAAFAgQEBAQEBAUHCAgICAgGBAQEBAQEAQgICAgIAQQEBAQEBAYICAgICAcFBAQEBAQE
BwgICAgIAQQEBAQEBAMICAgICAgFBAIkCwsLCwsLAD09PQYGBgYGBgYGBTtCQkIfHx8WFRUVFRUV
FRUVFRVAQz09PT09PQYGBQkLCwsLCwsMAwgICAgIBQQEBAQEBQcICAgICAMEBAQEBAQBCAQEBAQE
BAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFAgQEBAQCAAcHBwcAAQIEBAQEAgMA
BwcHBwAEBAIjCwsLCwsLCgUGBgYGBgYGBgYGBT9AFRUVFRUVFhUVFRUVFRUVFRVAQQQGBgYGBgYG
BBgLCwsLCwsMAQcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBAAQEBAQEBAUABwcHBwAGAgQEBAQC
CAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAIjCwsLCwsL
CgUGBgYGBgYGBgYGBTsUHx8VFRUfHx8fHx8fHx8fHx8fPAICAj0+Pj4+PhgLCwsLCwsvAQcHBwcA
BAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYA
BwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAIjCwsnAAoKBgYGBgYGBgYGBgYGBA01
KRoUFRQTKSkpKSkpKSkpKSkpNjc3IDg5OTk5OToLCwsKAAAABwcHBwcABAQEBAQEBQAHBwcHAAMC
BAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcH
BwcHAQIEBAQEAgMABwcHBwAEBAIjCwsnAgUFBgYGBgYGBgYGBgYGBAwLCywfFRQ0CwsLCwsLCwsL
CwsLCwsLCx8VFRUVFioLCwsGAgIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwIEBAQEBAUA
BwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFAgQEBAQCAAcHBwcAAQIEBAQEAgMABwcH
BwAEBAIjCwsnAgYGBgYGBgYGBgYGBgYGBAwLCzIfFBQzCwsLCwsLCwsLCwsLCwsLCx8VFRQUFCoL
CwsGAgIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBAAQFBQUFBAUICAgICAgGBAUFBQUEAQgI
CAgIAQQFBQUFBAYICAgICAgFBAUFBQUECAgICAgIAwQFBQUFBAMICAgICAgFBQIjCwsnAgYGBgYG
BgYGBgYGBgYGBAwLCyEcHC0uLy8wCwsLHBwcHBwcHBwcHBQVFh4cMRELCwsDBAQDCAgICAgIBQQF
BQUEBQgICAgICAMEBQUFBQQBCAAAAAAAAAECAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgIC
AgIBAAAAAAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAEkCwsnAgYGBgYGBgYGBgYGBgYGBAwLCwsL
CwsJAwYNCwsLHxQUFBQUFBQUFBUVFBcLCwsLCwsKBwAGAgICAgICBwAAAAAACAICAgICAgYAAAAA
AAAFAgcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQE
BgAHBwcHAAYEBAQEBAIHBwEkCwsnAgYGBgYGBgYGBgYGBgYGBAwLCwsLCwsJCAENCwsLHxUVFRUV
FRUVFhUVFBcLCwsLCwsKBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQE
BAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIH
BwEkCwsnAgUFBQUFBQUFBQYGBgYGBAwLCwsgIB0JCAENCwsLHxUVFRUVFRUVFRUVFBcLCywgIB0A
BwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQE
BAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwEkCwsnAgQEBAQEBAQE
BAYGBgYGBAwLCx0FAwMIBwENCwsLHxUVFRUVFRUVFRUVFBcLCxIFAwMHBwAGAgQEBAQCCAcHBwcH
CAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIB
BwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwEkCwsnAgQEBAQEBAQEBAYGBgYGAgwLCywDBwcH
BwENCwsLHxUVFRUVFRUVFRUVFBcLCxIDBwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAF
BAcAAAAAAAECAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAAAAAAAAgICAgICBQAA
AAAAAAYCAgICAgIHAAEkCwsnAgQEBAQEBAQEBAYGBgICAgwLCwsBBwAAAAENCwsLKx8fFhUVFRUV
FRUVFBcLCxIDAAAAAAAGAgICAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgMDAwMDAwMGBgYGBgYD
AwMDAwMDBgYGBgYGBgMDAwMDAwMGBgYGBgYDAwMDAwMDBgYGBgYGBgMDAwMDAwMGBgYGBgYDAwUk
CwsnAgQEBAQEBAQEBAQEAg4nJyQKGBgGAwMDAwUNCwsLKCgpKhYVFRUVFRUVFBcLCxIEAwMDAwMD
BgYGBgYGAwMDAwMDAwYGBgYGBgMDAwMDAwMDBgICAgICAgUAAAAAAAAGAgICAgICCAAAAAAABwIC
AgICAgYAAAAAAAAFAgICAgICAAAAAAAAAQICAgICAgMAAAAAAAAEAgIjCwsnAgQEBAQEBAQEBAQE
AicLCyQDCAgCAgICAgImCwsLCwsLHhQVFRUVFRUVFBcLCxICAgICAgIDAAAAAAAABAICAgICBAAA
AAAAAAMCAgICAgIBAAQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQE
BAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAIkCwsnAgICAgQEBAQEAgICAicLCyUBBwcCBAQEBAIm
CwsLCwsLHhYVFRUVFRUVFBcLCxICBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQE
BAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQE
AgMABwcHBwAEBAIJIyMjDAwMAwIEBAQCAwwMDSQkJSYBBwcCBAQEBAIYJSQkCwsLHhYVFRUVFRUV
FBcLCxICBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQE
BAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQCAgIK
CwsLAAIEBAQCAAsLCxgDAQEHBwcCBAQEBAQFAQMDCwsLHhYVFRUVFRUVFBcLCxICBAQEBAIDAAcH
BwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQE
AgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAIKCwsLAAICAgICAAsLCxgI
BwcHBwcCBAQEBAQGAAcHCwsLHhYVFRUVFRUVFBcLCxICBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcH
AAMCBAQEBAIBBwICAgICAgUAAAAAAAAGAgICAgICCAAAAAAABwICAgICAgYAAAAAAAAFAgICAgIC
AAAAAAAAAQICAgICAgMAAAAAAAAEAgICAgIKCx0LCgMBAQEDCiEiIRgHAAAAAAcCAgICAgIGAAcH
CwsLHhYVFRUVFRUVFBcLCxICAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAEBAQEB
CAEFBQUFBQUDCAEBAQEIBQUFBQUFBQgBAQEBCAMFBQUFBQUDCAEBAQEIBQUFBQUFBggBAQEBCAYF
BQUFBQUBAQEBAQgDAgICHQsLCwsLHQIGBgUFBQUFBQUIAQEBAQgDBQUFCwsLHhYVFRUWFRUVFBcL
CxIGAQEBAQgGBQUFBQUFAQEBAQEIAQUFBQUFBQYIAQEBAQgGBQcHBwcHAAECBAQEBAIDAAcHBwcA
BAQEBAQEBAAHBwcHAAMCBAQEBAIBAAcHBwcAAgQEBAQCBQAHBwcHAAYCBAQEBAIHBwcHBwAIAgIC
IAsLCwsLIAMHAAUCBAQEBAQABwcHBwADAgICCwsLHhYVFRUVFRUVFBcLCxIDBwcHBwAGAgQEBAQC
CAAHBwcACAIEBAQEAgYABwcHBwAFAgcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMC
BAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCHQsLCwsLHQMHAAUEBAQE
BAQABwcHBwADAgICCwsLHh8fFBUVFRUVFBcLCxIDBwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYA
BwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQE
BAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQCChgYGAkJCQgHAAUEBAQEBAQABwcHBwADAgQCGBgK
GRobHBQVFRUVFBcLCxIDBwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwEC
BAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQE
BAIHBwcHBwcIAgQEAgICBggICAcHAAUEBAQEBAQABwcHBwADAgQEAgICDgsLExQVFRUVFBcLCxID
BwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQE
BAQEBAAHBwcHAAMCBAQEBAIBAAcHBwcAAgQEBAQEBgAHBwcHAAYCBAQEBAIHBwcHBwcIAgQEBAQC
AwAHBwcHAAUEBAQEBAQABwcHBwADAgQEBAQCDgsLExQVFRUVFBcLCxIDBwcHBwAGAgQEBAQCCAcH
BwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAQDBwcHBwcHBQQEBAQEBAcHBwcHBwMEBAQE
BAIBBwcHBwcHAgQEBAQEBgcHBwcHBwYEBAQEBAIIBwcHBwcBAgQEBAQEAwcHBwcHBwUEBAQEBAQH
BwcHBwcDBAQEBAQCDgsLExQVFRUVFBcLCxIDBwcHBwcGBAQEBAQCCAcHBwcHCAIEBAQEBAYHBwcH
BwcFBAICAgICAgUAAAAAAAAGAgICAgICCAAAAAAABwICAgICAgYAAAAAAAAFAgICAgICAAAAAAAA
AQICAgICAgMAAAAAAAAEAgICAgIFAAAAAAAAAwICAgICAggAAAAAAAcCAgICAgIGAAAAAAADDgsL
ExQVFRUVFBcLCxICAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAQEBAQEBAUABwcH
BwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAE
BAQEBAQFAAcHBwcAAwIEBAQEAggHBwcHBwcCBAQEBAQGAAcHBwcDDgsLExQVFhUVFBcLCxICBAQE
BAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcH
CAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcHBwcAAwIE
BAQEAggHBwcHBwcCBAQEBAQGAAcHBwcDDgsLDxAQEBAQEBELCxICBAQEBAIDAAcHBwcABAQEBAQE
BQAHBwcHAAMCBAQEBAIBBwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAF
BAQEBAQCAAcHBwcHAQIEBAQEAgMABwcHBwAEBAQEBAQFAAcHBwcAAwIEBAQEAggHBwcHBwcCBAQE
BAQGAAcHBwcHAgICCQsLCwsLCw0GAQMCBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIB
BwQEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAQEBAQCAAcHBwcHAQIE
BAQEAgMABwcHBwAEBAQEBAQFAAcHBwcAAwIEBAQEAggHBwcHBwcCBAQEBAQGAAcHBwcABQICCQsL
CwsLCw0BBwECBAQEBAIDAAcHBwcABAQEBAQEBQAHBwcHAAMCBAQEBAIBBwICBAQEAgUAAAAAAAAG
AgQEBAQCCAAAAAAABwIEBAQEAgYAAAAAAAAFAgQEBAQCAAAAAAAAAQIEBAQEAgMAAAAAAAAEAgQE
BAIFAAAAAAAAAwIEBAQEAggAAAAAAAcCBAQEBAIGAAAAAAAABQICCQsLCwsLCwwBAAECBAQEBAID
AAAAAAAABAIEBAQCBAAAAAAAAAMCBAQEBAIBAAYGBgYGBgYDAwMDAwMGBgYGBgYGAwMDAwMDAwYG
BgYGBgYDAwMDAwMGBgYGBgYGAwMDAwMDAwYGBgYGBgMDAwMDAwMGBgYGBgYGAwMDAwMDAwYGBgYG
BgMDAwMDAwMGBgYGBgYGAwMDAwMDBgYGAAkJCQkJCQoDAwMGBgYGBgYDAwMDAwMDBgYGBgYGBgMD
AwMDAwMGBgYGBgYDAwAAAAAAAAECAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAAA
AAAAAgICAgICBQAAAAAAAAYCAgICAgIHAAAAAAAIAgICAgICAwAAAAAAAAUCAgICAgQAAAAAAAAD
AgICAgICAQAABwgICAICAgICAgUAAAAAAAAGAgICAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgcH
BwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcH
AAYEBAQEBAIHBwcHBwcIAgQEBAQCAwAHBwcHAAUEBAQEBAQABwcHBwADAgQEBAQCAQcHBwcHAAIE
BAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcH
BwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcI
AgQEBAQCAwAHBwcHAAUEBAQEBAQABwcHBwADAgQEBAQCAQcHBwcHAAIEBAQEBAUABwcHBwAGAgQE
BAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcH
AAMCBAQEBAIBBwcHBwcHAgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQEBAQCAwAHBwcHAAUE
BAQEBAQABwcHBwADAgQEBAQCAQcHBwcHAAIEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQE
AgYABwcHBwAFBAcHBwcHBwECBAQEBAIDAAcHBwcABQQEBAQEBAAHBwcHAAMCBAQEBAIBBwcHBwcH
AgQEBAQEBgAHBwcHAAYEBAQEBAIHBwcHBwcIAgQEBAQCAwAHBwcHAAUEBAQEBAQABwcHBwADAgQE
BAQCAQcHBwcHAAIEBAQEBAUABwcHBwAGAgQEBAQCCAcHBwcHCAIEBAQEAgYABwcHBwAFBAAAAAAA
AAECAgICAgIDAAAAAAAABAICAgICBAAAAAAAAAMCAgICAgIBAAAAAAAAAgICAgICBQAAAAAAAAYC
AgICAgIHAAAAAAAIAgICAgICAwAAAAAAAAUCAgICAgQAAAAAAAADAgICAgICAQAAAAAAAAICAgIC
AgUAAAAAAAAGAgICAgICBwAAAAAACAICAgICAgYAAAAAAAAFAgAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
"""
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
