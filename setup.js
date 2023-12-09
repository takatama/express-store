const bcrypt = require('bcrypt')
const sqlite3 = require('sqlite3')

const DATABASE_FILE = 'app.db'
const EVIL_DATABASE_FILE = 'evil.db'

const dbRun = (db, query, params = []) => new Promise((resolve, reject) => {
    db.run(query, params, function(err) {
        if (err) reject(err);
        else resolve(this);
    });
});

const dbAll = (db, query, params = []) => new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
    });
});

const dbClose = (db) => new Promise((resolve, reject) => {
    db.close((err) => {
        if (err) reject(err);
        else resolve();
    });
});

function getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1) + min); //The maximum is inclusive and the minimum is inclusive
}

async function setupDatabase() {
    const hashedPasswords = []
    for (let i = 1; i <= 9; i++) {
        hashedPasswords.push(await bcrypt.hash('password' + i, 10))
    }

    const db = new sqlite3.Database(DATABASE_FILE)
    await dbRun(db, 'DROP TABLE IF EXISTS products;')
    await dbRun(db, 'CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, description STRING, image_url STRING, price_yen INTEGER);')
    // 9つの商品を登録する。
    for (let i = 1; i <= 9; i++) {
        await dbRun(db, 
            'INSERT INTO products (name, description, image_url, price_yen) values (?, ?, ?, ?);', 
            [
                '商品' + i,
                '商品' + i + 'の説明',
                'https://via.placeholder.com/150',
                getRandomIntInclusive(1, 100) * 100
            ]
        )
    }

    await dbRun(db, 'DROP TABLE IF EXISTS users;')
    await dbRun(db, 'CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, email STRING, hashed_password STRING, nickname STRING);')
        // 9人のユーザーを登録する。
    for (let i = 1; i <= 9; i++) {
        await dbRun(db, 
            'INSERT INTO users (email, hashed_password, nickname) values (?, ?, ?)',
            [
                'user' + i + '@example.com',
                hashedPasswords[i - 1],
                'ユーザー' + i
            ]
        )    
    }

    await dbRun(db, 'DROP TABLE IF EXISTS reviews;')
    await dbRun(db, 'CREATE TABLE reviews(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, user_id INTEGER, rate INTEGER, comment STRING, foreign key(product_id) references products(id), foreign key(user_id) references users(id))')
    for (let i = 1; i <= 9; i++) {
        const productId = getRandomIntInclusive(1, 9)
        const userId = getRandomIntInclusive(1, 9)
        const rate = getRandomIntInclusive(1, 6)
        const comment =  '...'
        await dbRun(db, 
            'INSERT INTO reviews (product_id, user_id, rate, comment) values (?, ?, ?, ?)',
            [productId, userId, rate, comment]
        )
    }

    await dbRun(db, 'DROP VIEW IF EXISTS rated_products;')
    await dbRun(db, 'CREATE VIEW rated_products as SELECT p.id, p.name, p.description, p.image_url, p.price_yen, IFNULL(ROUND(AVG(r.rate), 1), "無し") FROM products AS p LEFT OUTER JOIN reviews AS r ON p.id = r.product_id GROUP BY p.id')

    console.log(await dbAll(db, 'SELECT * FROM products'));
    console.log(await dbAll(db, 'SELECT * FROM users'));
    console.log(dbAll(db, 'SELECT * FROM reviews'));
    console.log(await dbAll(db, 'SELECT * FROM rated_products'));
    await dbClose(db);

    evilDb = new sqlite3.Database(EVIL_DATABASE_FILE)
    await dbRun(evilDb, 'DROP TABLE IF EXISTS users;')
    await dbRun(evilDb, 'CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, datetime STRING, email STRING, password STRING);')
    await dbClose(evilDb);
}

setupDatabase().catch(console.error);
