<?php

$login = $_GET['uname'];
$pawo = $_GET['pw'];

$uname="tbattist_cogdev";
$pw="balre";
$database="tbattist_cat";

mysql_connect(localhost, $uname, $pw);
mysql_select_db($database);


$query = sprintf("SELECT pw from subjects where s_id = %s", $login) ;

$result = mysql_query($query);

$dbpw = mysql_result($result, 0);

if (strcmp($pawo,$dbpw)==0) {
	echo 1;
}
else {
	echo 0;
}

?>
