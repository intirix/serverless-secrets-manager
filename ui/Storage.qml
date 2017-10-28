import QtQuick 2.0
import QtQuick.LocalStorage 2.0

Item {
    function hasItem(key) {
        var db = openDb();
        var ret = false;
        db.transaction(
            function(tx) {
                var rs = tx.executeSql('SELECT val FROM Storage WHERE key = ?', [key]);
                if (rs.rows.length===1) {
                    ret = true;
                }
            }
        );
        return ret;
    }

    function getItem(key,def) {
        var db = openDb();
        var ret = def;
        db.transaction(
            function(tx) {
                var rs = tx.executeSql('SELECT val FROM Storage WHERE key = ?', [key]);
                console.log("Found "+rs.rows.length+" rows for "+key);
                if (rs.rows.length===1) {
                    ret = rs.rows.item(0).val;
                    //console.log("Using stored value "+ret+" for "+key)
                }
            }
        );
        return ret;
    }

    function setItem(key,val) {
        console.log("Saving setting "+key+"="+val);
        var db = openDb();
        db.transaction(
            function(tx) {
                tx.executeSql('DELETE FROM Storage WHERE key=?',[key]);
                tx.executeSql('INSERT INTO Storage (key,val) VALUES (?,?)', [key,val]);
            }
        );
    }

    function remoteItem(key) {
        console.log("Removing setting "+key);
        var db = openDb();
        db.transaction(
            function(tx) {
                tx.executeSql('DELETE FROM Storage WHERE key=?',[key]);
            }
        );
    }

    function openDb() {
        var db = LocalStorage.openDatabaseSync("CloudPasswordManagerStorage", "1.0", "Cloud Password Manager App", 100000);
        db.transaction(
            function(tx) {
                tx.executeSql('CREATE TABLE IF NOT EXISTS Storage(key TEXT, val TEXT)');
            }
        );
        return db;
    }


}
