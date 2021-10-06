const path = require("path");

const exportPath = path.resolve(__dirname, "Public")
module.exports = {
  entry: "./build/main.js",
  output: {
    filename: "main.js",
    path: exportPath
  },
  mode: "production"
}

module.exports = {
  entry: "./build/style.css",
  output: {
    filename: "style.css",
    path: exportPath
  },
  mode: "production"
}