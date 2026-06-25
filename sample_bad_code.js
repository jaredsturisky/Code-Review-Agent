// Bad because it has hardcoded secrets, unsafe command execution,
// no input validation, weak auth, and exposes raw server errors.

const express = require("express");
const app = express();

app.use(express.json());

const ADMIN_TOKEN = "admin-secret-token-123";
const BACKUP_PASSWORD = "BackupPassword123";

app.post("/backup-user", (req, res) => {
  const userId = req.body.userId;

  // Weak auth: compares request body directly to a hardcoded admin token
  if (req.body.token === ADMIN_TOKEN) {
    // Bad practice: logging sensitive values
    console.log("Backup password:", BACKUP_PASSWORD);

    // Dangerous: userId is inserted directly into a shell command
    const command = `tar -czf /backups/${userId}.tar.gz /users/${userId}`;

    require("child_process").exec(command, (error, stdout) => {
      if (error) {
        // Bad practice: exposes internal stack trace to client
        return res.status(500).send(error.stack);
      }

      res.send("Backup complete: " + stdout);
    });
  } else {
    res.status(403).send("Invalid token");
  }
});

app.listen(3000);