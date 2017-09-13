import QtQuick 2.0

Item {
    property var defaultUrl: "https://example.com/v1"
    property var host: ""
    property var basePath: ""
    property var user: storage.getItem("lastUser","admin")
    property var pass: ""
    property var token: ""

    Component.onCompleted: {
        var url = storage.getItem("lastUrl",defaultUrl);
        console.log("Setting default url to "+url)
        setUrl(url);
    }

    Storage {
        id: storage
    }

    function setUser(val) {
        user = val
        storage.setItem("lastUser",val);
    }

    function setUrl(url) {
        storage.setItem("lastUrl",url);
        host = getLocation(url).protocol+"//"+getLocation(url).hostname
        basePath = getLocation(url).pathname;
    }

    function getUrl() {
        return host + basePath;
    }

    // https://stackoverflow.com/questions/736513/how-do-i-parse-a-url-into-hostname-and-path-in-javascript
    function getLocation(href) {
        var match = href.match(/^(https?\:)\/\/(([^:\/?#]*)(?:\:([0-9]+))?)([\/]{0,1}[^?#]*)(\?[^#]*|)(#.*|)$/);
        return match && {
            href: href,
            protocol: match[1],
            host: match[2],
            hostname: match[3],
            port: match[4],
            pathname: match[5],
            search: match[6],
            hash: match[7]
        }
    }
}
