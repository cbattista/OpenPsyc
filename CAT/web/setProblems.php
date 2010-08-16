<?php

$uname="tbattist_cogdev";
$pw="balre";
$database="tbattist_cat";

mysql_connect(localhost, $uname, $pw);
mysql_select_db($database);

$n1 = $_GET["n1"];
$n2 = $_GET["n2"];
$rt = $_GET["RT"];
$acc = $_GET["ACC"];
$subject = $_GET["subject"];
$resp = $_GET["RESP"];

$query = sprintf("INSERT INTO training_data (n1, n2, RESP, RT, ACC, s_id) VALUES (%s, %s, %s, %s, %s, %s);", $n1, $n2, $resp, $rt, $acc, $subject);

$result = mysql_query($query);

?>
