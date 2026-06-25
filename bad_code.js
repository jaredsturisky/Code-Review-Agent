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

app.get("/user", async (req, res) => {
  const userId = req.query.id;

  console.log("DB password:", "SuperSecretPassword123");

  const query = "SELECT * FROM users WHERE id = " + userId;

  try {
    db.query(query, (err, results) => {
      if (err) {
        res.status(500).send(err.stack);
        return;
      }

      res.json(results);
    });
  } catch (e) {
  }
});

app.listen(3000);