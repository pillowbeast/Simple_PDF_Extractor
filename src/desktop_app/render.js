const { ipcRenderer } = require('electron');

// Buttons
const loadBtn = document.getElementById('loadBtn');
const saveBtn = document.getElementById('saveBtn');
const convertBtn = document.getElementById('convertBtn');

let LoadedFile = null;
let OutputFile = null;
let Flags = null;
let language = null; // 'en-US';
let speed = null; // 1.0;
let awsAccessKeyId = null;
let awsSecretKey = null;
let voice = null; // 'Microsoft Zira Desktop - English (United States)';
let volume = null; // 1.0;


// Open windows files when button loadBtn is clicked
loadBtn.addEventListener('click', async function (event) {
    console.log('loadBtn clicked');
    ipcRenderer.send('load-file');    
});

// ipcRenderer.on will receive the “file-loaded” info from mainprocess
ipcRenderer.on('file-loaded', function (event, arg) {
    console.log('file-loaded');
    LoadedFile = arg;
    console.log("filePath:", LoadedFile);
});

// Convert file when button convertBtn is clicked
convertBtn.addEventListener('click', function (event) {
    console.log('convertBtn clicked');
    // show message if no file is selected
    if (LoadedFile === null) {
        alert('Please select a file');
        return;
    }
    // send info to mainprocess
    // Create Object with all the info
    var info = {
        '-m': 'txt',
        '-n': LoadedFile,
        '-o': OutputFile,
        '-f': Flags,
        '-l': language,
        '-s': speed,
        '-i': awsAccessKeyId,
        '-k': awsSecretKey,
        '-v': voice,
        '--volume': volume,
    }
    ipcRenderer.send('convert-file', info);
});

// ipcRenderer.on will receive the “file-converted" info from mainprocess
ipcRenderer.on('file-converted', function (event, arg) {
    console.log('file-converted');
    console.log(arg);
});

// Save file when button saveBtn is clicked
saveBtn.addEventListener('click', function (event) {
    console.log('saveBtn clicked');
    console.log("filePath:", LoadedFile);
    ipcRenderer.send('save-file');
});

