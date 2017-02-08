<?php
/**
 * Created by PhpStorm.
 * User: alper
 * Date: 9/23/16
 * Time: 1:58 PM
 */
require_once('db.php');

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['id'])) {
        // Create connection
        $conn = new mysqli($server, $username, $password, $db);

// Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }
        $id = $_POST['id'];

        if ($stmt = $conn->prepare("UPDATE songs SET restricted=1 WHERE id=?")) {
            /* BK: always check whether the prepare() succeeded */

            $stmt->bind_param('i', $id);

            /* Execute the prepared Statement */
            $status = $stmt->execute();
        }
        $stmt->close();
        $conn->close();
        echo 'success';
    }
}