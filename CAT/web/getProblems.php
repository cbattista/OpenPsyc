<?php

$subject = $_GET['subject'];

$uname="tbattist_cogdev";
$pw="balre";
$database="tbattist_cat";


mysql_connect(localhost, $uname, $pw);
mysql_select_db($database);

$query = sprintf("SELECT n1, n2 FROM training_sets WHERE s_id = %s", $subject);

$result = mysql_query($query);

while ($row = mysql_fetch_assoc($result)) {
    $n1 = $row['n1'];
    $n2 = $row['n2'];
	$output.= sprintf("%s|%s,", $n1, $n2);
}

$output = substr($output, 0, -1);

echo $output;

?>
