const { ipcRenderer } = require('electron');

// Buttons
const loadBtn = document.getElementById('loadBtn');
const convertTxt = document.getElementById('convertTxt');
const saveTxt = document.getElementById('saveTxt');
const convertMp3 = document.getElementById('convertMp3');
const saveMp3 = document.getElementById('saveMp3');

let LoadedFile = null;
let OutputFile = null;
let Flags = null;
let language = null; // 'en-US';
let speed = null; // 1.0;
let awsAccessKeyId = null;
let awsSecretKey = null;
let voice = null; // 'Microsoft Zira Desktop - English (United States)';
let volume = null; // 1.0;
let txt_converted = null;
let mp3_converted = null;


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

// Convert file when button convertTxt is clicked
convertTxt.addEventListener('click', function (event) {
    console.log('convertTxt clicked');
    // show message if no file is selected
    if (LoadedFile === null) {
        alert('Please select a file');
        return;
    }
    // send info to mainprocess
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
    ipcRenderer.send('convert-txt', info);
});

// Convert file when button convertMp3 is clicked
convertMp3.addEventListener('click', function(event) {
    console.log('convertMp3 clicked');
    // show message if no pdf has been converted to txt or if loaded file is not .txt

    // send info to mainprocess
    var info = {
        '-m': 'mp3',
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
    ipcRenderer.send('convert-mp3', info);
})

// ipcRenderer.on will receive the “converted-txt" info from mainprocess
ipcRenderer.on('converted-txt', function (event, arg) {
    console.log(arg);
    console.log('converted-txt');
    
    filename = LoadedFile.split('\\').pop();
    n = filename.split('.').shift();

    txt_converted = 'temp\\' + n + '.txt';
    console.log(txt_converted)
});

// ipcRenderer.on will receive the “converted-mp3" info from mainprocess
ipcRenderer.on('converted-mp3', function (event, arg) {
    console.log(arg);
    console.log('converted-mp3');

    filename = LoadedFile.split('\\').pop();
    n = filename.split('.').shift();

    txt_converted = 'temp\\' + n + '.mp3';
    console.log(mp3_converted)
});

// Save file when button saveTxt is clicked
saveTxt.addEventListener('click', function (event) {
    console.log('saveTxt clicked');
    console.log('temp dir:', txt_converted)
    ipcRenderer.send('save-txt', txt_converted);
});

// Save file when button saveMp3 is clicked
saveMp3.addEventListener('click', function (event) {
    console.log('saveMp3 clicked');
    ipcRenderer.send('save-mp3', mp3_converted);
});

