from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

db_params = {
    "dbname": "football",
    "user": "postgres",
    "password": "Abhi@123",
    "host": "localhost",
    "port": "5432",
}

conn = None
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    print("Successfully connected to the database!")

    # Perform any database operations as needed

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")

def get_players_data(club_name=None, position=None):

    # Build the SQL query based on the provided parameters
    query = """
    SELECT members.fullname, members.age, footballclub.club_name, players.position
    FROM members
    JOIN footballclub ON members.club_id = footballclub.club_id
    JOIN players ON members.member_id = players.member_id
    WHERE (%s IS NULL OR footballclub.club_name = %s OR %s = '')
      AND (%s IS NULL OR players.position = %s OR %s = '');
    """

    # If no search parameters provided, retrieve all player data
    if club_name is None and position is None:
        query = """
        SELECT members.fullname, members.age, footballclub.club_name, players.position
        FROM members
        JOIN footballclub ON members.club_id = footballclub.club_id
        JOIN players ON members.member_id = players.member_id;
        """

        cursor.execute(query)
        player_data = cursor.fetchall()
    else:
        cursor.execute(query, (club_name, club_name, club_name, position, position, position))
        player_data = cursor.fetchall()

    print(player_data)

    return player_data


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/players", methods=["GET", "POST"])
def players():
    try:
        if request.method == "POST":
            club_name = request.form.get("club_name")
            position = request.form.get("position")
            print(f"Search Parameters - Club Name: {club_name}, Position: {position}")
            players_data = get_players_data(club_name, position)
        else:
            # Default: Load all player data
            players_data = get_players_data()

        print("Returned Player Data:", players_data)
        return render_template("players.html", players=players_data)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("error.html", error_message=str(e))


# def filter_players_by_club(club_name):
#     players_data = get_players_data()
#     filtered_players = [player for player in players_data if player[2].lower() == club_name.lower()]
#     return filtered_players

def get_national_team_players(nation_name=None, position=None):

    # Build the SQL query based on the provided parameters
    query = """
    SELECT members.fullname, members.age, nations.nation_name, players.position
    FROM members
    JOIN players ON members.member_id = players.member_id
    JOIN playsnation ON members.member_id = playsnation.member_id
    JOIN nations ON playsnation.nation_id = nations.nation_id
    WHERE (%s IS NULL OR nations.nation_name = %s OR %s = '')
      AND (%s IS NULL OR players.position = %s OR %s = '');
    """

    # If no search parameters provided, retrieve all national team player data
    if nation_name is None and position is None:
        query = """
        SELECT members.fullname, members.age, nations.nation_name, players.position
        FROM members
        JOIN players ON members.member_id = players.member_id
        JOIN playsnation ON members.member_id = playsnation.member_id
        JOIN nations ON playsnation.nation_id = nations.nation_id;
        """

        cursor.execute(query)
        national_team_players_data = cursor.fetchall()
    else:
        cursor.execute(query, (nation_name, nation_name, nation_name, position, position, position))
        national_team_players_data = cursor.fetchall()


    return national_team_players_data

@app.route("/national_team_players", methods=["GET", "POST"])
def national_team_players():
    try: 
        if request.method == "POST":
            nation_name = request.form.get("nation_name")
            position = request.form.get("position")
            print(f"Search Parameters - Nation Name: {nation_name}, Position: {position}")
            national_team_players_data = get_national_team_players(nation_name, position)
        else:
            # Default: Load all national team player data
            national_team_players_data = get_national_team_players()

        print("Returned National Team Player Data:", national_team_players_data)
        return render_template("national_team_players.html", national_team_players=national_team_players_data)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("error.html", error_message=str(e))

def get_football_club_data():

    # Build the SQL query to retrieve football club data
    query = """
    SELECT club_name, estyear, playsintournament, city_country
    FROM footballclub;
    """

    cursor.execute(query)
    football_club_data = cursor.fetchall()

    return football_club_data


@app.route("/football_clubs", methods=["GET"])
def football_clubs():
    football_club_data = get_football_club_data()
    return render_template("football_clubs.html", football_club_data=football_club_data)

def get_trophies_data(trophy_name=None, trophy_year=None):

   # Build the SQL query to retrieve trophy data with optional filters
    query = """
    SELECT trophies.trophy_name, COALESCE(footballclub.club_name, nations.nation_name) AS won,
           trophies.trophy_year
    FROM trophies
    LEFT JOIN footballclub ON trophies.club_id = footballclub.club_id
    LEFT JOIN nations ON trophies.nation_id = nations.nation_id
    WHERE (%s IS NULL OR trophies.trophy_name = %s)
       AND (%s IS NULL OR trophies.trophy_year = %s);
    """

    # Use 'None' for NULL values in the execute function
    cursor.execute(query, (trophy_name, trophy_name, trophy_year, trophy_year))
    trophies_data = cursor.fetchall()

    return trophies_data

@app.route("/trophies", methods=["GET", "POST"])
def trophies():
    if request.method == "POST":
        trophy_name = request.form.get("trophy_name")
        trophy_year = request.form.get("trophy_year")
        #trophy_year = int(trophy_year) if trophy_year and trophy_year.strip() else None
        trophies_data = get_trophies_data(trophy_name, trophy_year)
    else:
        trophies_data = get_trophies_data()
    return render_template("trophies.html", trophies_data=trophies_data)

if __name__ == "__main__":
    try:
        app.run(host="127.0.0.1", port=5000, debug=True)
    except Exception as e:
        print(f"Flask app error: {e}")
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

