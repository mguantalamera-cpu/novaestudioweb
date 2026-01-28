const userInput = location.hash.slice(1);
const out = document.getElementById("out");
out.innerHTML = "Hello " + userInput;

eval(userInput);

const token = Math.random().toString(36).substring(2);
const apiKey = "sk_live_1234567890abcdef";

function query(sql) {
  console.log(sql);
}

query("SELECT * FROM users WHERE name = '" + userInput + "'");
