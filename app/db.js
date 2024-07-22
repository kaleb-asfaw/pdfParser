// db.js
module.paths.push('/usr/lib/node_modules')

const mysql = require('mysql');
const bcrypt = require('bcrypt');

let connection;

function getConnection() {
  if (connection == null) {
    connection = new Promise((resolve, reject) => {
      const conn = mysql.createConnection({
        host: 'localhost',
        user: 'codio',
        password: 'codiopassword',
        database: 'codio'
      });

      conn.connect(function(err) {
        if (err) {
          reject(err)
        } else {
          resolve(conn)
        }
      })     
    })
  }
  return connection;
}

function findPasswordSalt(login) {
  return getConnection()
  .then(conn => {
    return new Promise((resolve, reject) => {
      conn.query('SELECT login, pwdhash FROM users WHERE login = ?', [login], (error, results, fields) => {
        if (error) {
          reject(error)
        } else {
          resolve(results && results[0])
        }
      });
    });
  });
}

function createUserEntry(login, password) {
  return bcrypt.hash(password, 10).then(hash => {
    return getConnection()
    .then(conn => {
      return new Promise((resolve, reject) => {
        conn.query('INSERT INTO users (login, pwdhash) VALUES(?, ?)', [login, hash], (error, results) => {
          if (error) {
            reject(error)
          } else {
            resolve(results)
          }
        });
      });
    });
  });
}

module.exports = { createUserEntry, findPasswordSalt }
