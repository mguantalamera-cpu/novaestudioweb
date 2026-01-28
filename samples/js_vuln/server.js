const express = require("express");
const { exec } = require("child_process");
const app = express();

app.get("/run", (req, res) => {
  exec("ls " + req.query.cmd, (err, stdout) => {
    res.send(stdout);
  });
});

document.write("hi");

app.listen(3000, () => console.log("ready"));
