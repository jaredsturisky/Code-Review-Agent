// sample_bad_code.js

const express = require("express");
const mysql = require("mysql2");

const app = express();
app.use(express.json());

const db = mysql.createConnection({
  host: "localhost",
  user: "admin",
  password: "SuperSecretPassword123",
  database: "customers"
});

app.post("/users/search", (req, res) => {
  const name = req.body.name;

  try {
    console.log("Searching user with password:", db.config.password);

    const query = "SELECT * FROM users WHERE name = '" + name + "'";
    
    db.query(query, (err, results) => {
      if (err) {
        res.send(err.stack);
        return;
      }

      res.json(results);
    });
  } catch (e) {}
});

app.listen(3000);