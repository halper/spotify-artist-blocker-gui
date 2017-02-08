<?php
/**
 * Created by PhpStorm.
 * User: alper
 * Date: 9/21/16
 * Time: 4:29 PM
 */

/*ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);*/

require_once('db.php');

// Create connection
$conn = new mysqli($server, $username, $password, $db);
mysqli_set_charset($conn, "utf8");
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$page = $_POST['page'];
$paginate_by = 10;
$start = (($page - 1) * $paginate_by) + 1;
$end = ($page * $paginate_by) + 1;

$my_resp['currentSong'] = get_current_song($conn);
$my_resp['songs'] = get_songs($conn, $start, $end);
$genre_and_data = get_genres_and_data($conn);

$my_resp['genres'] = $genre_and_data['genres'];
$my_resp['data'] = $genre_and_data['data'];
$my_resp['last_page'] = get_last_page($conn);
header('Content-Type: application/json');
echo json_encode($my_resp);

$conn->close();

function get_current_song($conn)
{
    $sql = "SELECT title, artist, album, cover FROM songs WHERE restricted = 0 ORDER BY played_on DESC LIMIT 0,1";
    $result = $conn->query($sql);
    $row = mysqli_fetch_assoc($result);
    $result->close();
    return $row;

}

function get_songs($conn, $start, $end)
{
    $songs = [];

    $sql = "SELECT s.id, s.title, s.artist, s.album, s.cover, s.played, s.duration, s.played_on, g.name
            FROM songs AS s, genres AS g
            WHERE s.restricted = 0 AND g.id = s.genre_id
            ORDER BY s.played_on DESC LIMIT $start,$end";

    foreach ($conn->query($sql) as $row) {

        $played_on = new DateTime($row['played_on']);
        $played_on = $played_on->format('H:i d.m.Y');
        array_push($songs, [
            'id' => $row['id'],
            'artist' => ucwords($row['artist']),
            'title' => ucwords(preg_replace('/-.*/i', '', $row['title'])),
            'album' => $row['album'],
            'cover' => $row['cover'],
            'count' => $row['played'],
            'played_on' => $played_on,
            'duration' => $row['duration'],
            'genre' => $row['name']
        ]);

    }

    return $songs;
}

function get_genres_and_data($conn){
    $genres = [];
    $data = [];

    foreach ($conn->query("SELECT * FROM genres") as $row) {
        array_push($genres, $row['name']);
        $g_id = $row['id'];
        $result = $conn->query("SELECT COUNT(*) FROM songs WHERE genre_id = $g_id AND restricted = 0");
        $count_row = $result->fetch_row();
        array_push($data, $count_row[0]);
        $result->close();
    }
    $my_arr['genres'] = $genres;
    $my_arr['data'] = $data;
    return $my_arr;
}

function get_last_page($conn){
    $result = $conn->query("SELECT COUNT(*) FROM songs WHERE restricted = 0");
    $count_row = $result->fetch_row();
    $last_page = (int)$count_row[0] / 20;
    $result->close();
    return ceil($last_page);
}