const path = require("path");

const exportPath = path.resolve(__dirname, "Public")
module.exports = {
  entry: "./build/main.js",
  output: {
    filename: "main.js",
    path: exportPath
  },
  mode: "development",
  // devtool: false
}

