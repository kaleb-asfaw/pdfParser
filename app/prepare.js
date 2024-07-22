module.paths.push('/usr/lib/node_modules')

const mysql = require('mysql')

function prepare() {
  const con = mysql.createConnection({
    host: 'localhost',
    user: 'codio',
    password: 'codiopassword',
    database: 'codio'
  });

  con.connect(function(err) {
    if (err) throw err;

    con.query('CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, login varchar(100) UNIQUE NOT NULL, pwdhash varchar(97) NOT NULL)', () => {
      con.end()
    })
  });
}

module.exports = { prepare }

// Run this script
prepare();
