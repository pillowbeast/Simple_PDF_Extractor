const {app, BrowserWindow} = require('electron')
const ui = require('./desktop_app/utilities/ui')

function createWindow () {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  })

  // Call the ui.createButton() function to create a button
  const button = ui.createButton('Click me')

  // Add the button to the window
  win.add(button)

  // and load the index.html of the app.
  win.loadFile('desktop_app/index.html')
}

app.whenReady().then(createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
