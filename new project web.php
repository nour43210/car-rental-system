<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Car Rental System</title>
    <style>
        body {
            background-color: #282828;
            color: white;
            font-family: Georgia, serif;
            text-align: center;
        }
        .welcome {
            margin-top: 100px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            font-size: 20px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="welcome">
        <h1>Welcome to Our Car Rental System</h1>
        <p>Click below to continue to rent a car.</p>
        <form action="register_customer.php" method="get">
            <button type="submit">Continue to Rent a Car</button>
        </form>
    </div>
</body>
</html>
