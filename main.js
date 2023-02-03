const { app, BrowserWindow, ipcMain, dialog, utilityProcess } = require('electron');
var fs = require('fs');
const path = require('path');

let mainWindow;

app.on('ready', () => {
    createWindow();
});

function createWindow () {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 1024, //500,
        height: 500,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    // and load the index.html of the app.
    mainWindow.loadFile(path.join(__dirname, 'src/desktop_app/index.html'));

    // Open the DevTools.
    mainWindow.webContents.openDevTools();

    mainWindow.on('closed', function () {
        mainWindow = null
    });
};

// app.on('before-quit', (event) => {
//     console.log('before-quit');
//     // Read the contents of the folder
//     const folder = path.join(__dirname, 'temp');
//     const files = fs.readdirSync(folder);

//     // Iterate over each file and delete it
//     files.forEach(file => {
//         const filePath = path.join(folder, file);
//         fs.unlinkSync(filePath);
//     });
// });


// Quit when all windows are closed.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

//ipcMain.on will receive the load-file info from renderprocess 
ipcMain.on("load-file", async function (event, arg) {
    const options = {
        title: 'Select a PDF file',
        defaultPath: __dirname,
        buttonLabel: 'Select',
        filters: [
            { name: 'PDF', extensions: ['pdf'] },
            { name: 'TXT', extensions: ['txt'] }
        ],
        properties: ['openFile']
    };
    const filepath = await dialog.showOpenDialog(null, options);
    // event.sender.send in ipcMain will return the reply to renderprocess
    event.sender.send("file-loaded", filepath.filePaths[0]); 
});

//ipcMain.on will receive the convert-file info from renderprocess
ipcMain.on("convert-txt", async function (event, arg) {
    var spawn = require("child_process").spawn;
    console.log("convert-txt:",arg);

    // Create command from dictionary
    var command = ['main.py']
    for (var key in arg) {
        var value = arg[key];
        if (value != null) {
            command.push(key);
            command.push(value);
        }
    }
    console.log("command:",command);
    
    var conversion = spawn('python',command);

    conversion.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        event.sender.send("converted-txt", data.toString());
    });
    
    conversion.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
    
    conversion.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
});

//ipcMain.on will receive the convert-file info from renderprocess
ipcMain.on("convert-mp3", async function (event, arg) {
    var spawn = require("child_process").spawn;
    console.log("convert-mp3:",arg);

    // Create command from dictionary
    var command = ['main.py']
    for (var key in arg) {
        var value = arg[key];
        if (value != null) {
            command.push(key);
            command.push(value);
        }
    }
    console.log("command:",command);
    
    var conversion = spawn('python',command);

    conversion.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        event.sender.send("converted-mp3", data.toString());
    });
    
    conversion.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
    
    conversion.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
});


//ipcMain.on will receive the save-txt info from renderprocess
ipcMain.on("save-txt", async function (event, arg) {
    // get name from arg
    filename = arg.split('\\').pop();

    const options = {
        title: 'Save Txt file',
        defaultPath: app.getPath('documents') + '\\' + filename,
        buttonLabel: 'Select',
        filters: [
            { name: 'TXT', extensions: ['txt'] }
        ],
    };
    const filepath = await dialog.showSaveDialog(null, options);
    console.log("save-txt:",filepath.filePath);
    // Move file from temp folder to selected location
    console.log("arg:",arg);
    data = fs.readFileSync(arg);
    fs.writeFileSync(filepath.filePath, data);
    // event.sender.send in ipcMain will return the reply to renderprocess
    event.sender.send("saved-txt", filepath.filePath); 
});

//ipcMain.on will receive the save-mp3 info from renderprocess
ipcMain.on("save-mp3", async function (event, arg) {
    // get name from arg
    filename = arg.split('\\').pop();

    const options = {
        title: 'Save MP3 file',
        defaultPath: __dirname + '\\' + filename,
        buttonLabel: 'Select',
        filters: [
            { name: 'MP3', extensions: ['mp3'] }
        ],
    };
    const filepath = await dialog.showSaveDialog(null, options);
    console.log("save-mp3:",filepath.filePath)
    // Move file from temp folder to selected location
    fs.write(filepath.filePath, fs.read(arg));

    // event.sender.send in ipcMain will return the reply to renderprocess
    event.sender.send("saved-mp3", filepath.filePath); 
});

