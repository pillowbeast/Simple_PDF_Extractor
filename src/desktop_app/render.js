const { ipcRenderer } = require('electron');

// Buttons
const loadBtn = document.getElementById('loadBtn');
const saveBtn = document.getElementById('saveBtn');
const convertBtn = document.getElementById('convertBtn');

// Open windows files when button loadBtn is clicked
loadBtn.addEventListener('click', async function (event) {
    console.log('loadBtn clicked');
    ipcRenderer.send('load-file');    
});

// Save file when button saveBtn is clicked
saveBtn.addEventListener('click', function (event) {
    console.log('saveBtn clicked');
    ipcRenderer.send('save-file');
});

// Convert file when button convertBtn is clicked
convertBtn.addEventListener('click', function (event) {
    console.log('convertBtn clicked');
    ipcRenderer.send('convert-file');
});

// ipcRenderer.on will receive the “file-loaded” info from mainprocess
ipcRenderer.on('file-loaded', function (event, arg) {
    console.log('file-loaded');
    console.log(arg);
});

// ipcRenderer.on will receive the “file-converted" info from mainprocess
ipcRenderer.on('file-converted', function (event, arg) {
    console.log('file-converted');
    console.log(arg);
});