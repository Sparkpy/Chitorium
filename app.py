from leetifypy.scraper import WebScraper
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request, abort
from flask_mysqldb import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import random
import string
import matplotlib.pyplot as plt
from faker import Faker
fake = Faker()
def generate_random_filename():
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for _ in range(10))
    return f"{random_string}.png"
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'communitycharts'
app.config['API_TOKEN'] = "e]6=}s@qD+'Zra?v+pv)WRMJuO)ogyUMUR8Q93}VS814K-**w|zrqKZV52#uYI"
mysql = MySQL(app)

# Define the allowed IP address
allowed_ip = '127.0.0.1'
def get_client_ip():
    # Get the client's IP address from the X-Forwarded-For header
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    return ip_address
# Apply @app.before_request globally to check IP address before every request
limiter = Limiter(get_client_ip, app=app, default_limits=["200 per day", "2 per minute"], storage_uri="memory://")
@app.route("/")
@limiter.exempt
def test():
    return render_template("index.html")
@app.route("/leetify", methods=["GET", "POST"])
def dothescrape():
    print("hello!")
    url = request.form["link"]
    rnum = int(request.form["rec"])
    try:

        scraper = WebScraper()  


        player_name = scraper.get_player_name(url)
        player_winrate = scraper.get_player_winrate(url)
        teammates_dict = scraper.get_player_teammates(url)


        print(f"\nPlayer Name: {player_name}")
        print(f"Player Winrate: {player_winrate}%")

        G = nx.Graph()  

        if not G.has_node(player_name):
            G.add_node(player_name, url=url, winrate=player_winrate)
            G.nodes[player_name]['color'] = "green"
            G.nodes[player_name]['banned'] = scraper.get_banned(url)

        for name, teammate_url in teammates_dict.items():
            if not G.has_node(name):
                if(len(G.nodes) > rnum):
                    break
                if(name == ''):
                    name = scraper.get_player_name(teammate_url)
                winrate = scraper.get_player_winrate(teammate_url)
                winrate = winrate.rstrip("%")
                if not G.has_node(name):
                    G.add_node(name, url=teammate_url, winrate=winrate)


                if winrate == '':
                    G.nodes[name]['color'] = 'skyblue'
                elif int(winrate) > 80 or int(scraper.get_aim_stat(teammate_url)) > 80:
                    G.nodes[name]['color'] = 'red'
                elif int(winrate) > 65:
                    G.nodes[name]['color'] = 'yellow'
                else:
                    G.nodes[name]['color'] = 'skyblue'
                if (scraper.get_banned(teammate_url)):
                    G.nodes[name]['color'] = '#3a0000'
                    G.nodes[name]['banned'] = True
                else:
                    try:
                        sprof = scraper.get_player_steam_level(scraper.get_steam_profile_link(teammate_url))
                        if(sprof == "pvt" or int(sprof) < 15 and int(winrate) > 50):
                            G.nodes[name]['color'] = '#8B8000'
                    except Exception as e:
                        print(e)




            G.add_edge(player_name, name)  


        for name, teammate_url in teammates_dict.items():
            if(len(G.nodes) > rnum):
                break
            if(name == ''):
                name = scraper.get_player_name(teammate_url)
            print(f"\nChecking teammates for {name}:")
            try:
                sub_teammates_dict = scraper.get_player_teammates(teammate_url)

                for sub_name, sub_url in sub_teammates_dict.items():
                    if not G.has_node(sub_name):
                        if(len(G.nodes) > rnum):
                            break
                        if(sub_name == ''):
                            sub_name = scraper.get_player_name(sub_url)
                        print(f"\nChecking teammates for {sub_name} (Sub-Teammate of {name}):")


                    
                        G.add_node(sub_name, url=sub_url)  


                        G.add_edge(name, sub_name)


                        winrate = scraper.get_player_winrate(sub_url)
                        if (winrate == None):
                            winrate = scraper.get_player_winrate(sub_url).rstrip("%")
                        if (winrate.find("%")):
                            winrate = winrate.rstrip("%")
                        if winrate == '':
                            G.nodes[sub_name]['color'] = 'skyblue'
                        elif int(winrate) > 80 or int(scraper.get_aim_stat(sub_url)) > 80:
                            G.nodes[sub_name]['color'] = 'red'
                        elif int(winrate) > 65:
                            G.nodes[sub_name]['color'] = 'yellow'
                        else:
                            G.nodes[sub_name]['color'] = 'skyblue'

                        if (scraper.get_banned(sub_url)):
                            G.nodes[sub_name]['color'] = '#3a0000'
                            G.nodes[sub_name]['banned'] = True
                        else:
                            try:
                                ssprof = scraper.get_player_steam_level(scraper.get_steam_profile_link(sub_url))
                                if(ssprof == "pvt" or int(ssprof) < 15 and int(winrate) > 50):
                                    G.nodes[sub_name]['color'] = '#8B8000'
                            except Exception as e:
                                print(e)


                        G.nodes[sub_name]['winrate'] = winrate




                        G.add_node(sub_name, url=sub_url, winrate=winrate)
                        G.add_edge(name, sub_name)  


                    try:
                        sub_sub_teammates_dict = scraper.get_player_teammates(sub_url)

                        for sub_sub_name, sub_sub_url in sub_sub_teammates_dict.items():
                            if not G.has_node(sub_sub_name):
                                if(len(G.nodes) > rnum):
                                    break
                                if(sub_sub_name == ''):
                                    sub_sub_name = scraper.get_player_name(sub_sub_url)



                                G.add_edge(sub_name, sub_sub_name)



                            

                                winrate = scraper.get_player_winrate(sub_sub_url).rstrip("%")
                                if(winrate == '' or winrate == '%' or winrate == None or winrate == ' '):
                                    while winrate == '' or winrate == '%' or winrate == None or winrate == ' ':
                                        winrate = scraper.get_player_winrate(sub_sub_url)
                                winrate = winrate.rstrip("%")

                                try:
                                    winrate = int(winrate)
                                except Exception as e:
                                    print(e)
                                G.add_node(sub_sub_name, url=sub_sub_url, winrate=winrate)
                                G.add_edge(sub_name, sub_sub_name)  

                                if winrate:
                                    if int(winrate) > 80 or int(scraper.get_aim_stat(sub_sub_url)) > 80:
                                        G.nodes[sub_sub_name]['color'] = 'red'
                                    elif int(winrate) > 65:
                                        G.nodes[sub_sub_name]['color'] = 'yellow'
                                    else:
                                        G.nodes[sub_sub_name]['color'] = 'skyblue'
                                else:
                                    G.nodes[sub_sub_name]['color'] = 'skyblue'

                                if (scraper.get_banned(sub_sub_url)):
                                    G.nodes[sub_name]['color'] = '#3a0000'
                                    G.nodes[sub_sub_name]['banned'] = True
                                else:
                                    try:
                                        sssprof = scraper.get_player_steam_level(scraper.get_steam_profile_link(sub_sub_url))
                                        if(sssprof == "pvt" or int(sssprof) < 15 and int(winrate) > 50):
                                            G.nodes[name]['color'] = '#8B8000'
                                    except Exception as e:
                                        print(e)








                    except Exception as e:
                        print(f"An error occurred while processing sub-sub-teammates for {sub_name}: {e}")

            except Exception as e:
                print(f"An error occurred while processing sub-teammates for {name}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    pos = nx.spring_layout(G)
    colors = [data['color'] if 'color' in data else 'blue' for node, data in G.nodes(data=True)]

    nx.draw(G, pos, with_labels=True, node_size=700, node_color=colors, font_size=8, font_color='black', font_weight='bold', edge_color='black', arrowsize=10)


    for node, (x, y) in pos.items():
        try:
            if G.nodes[node]['winrate'] != '':
                plt.text(x, y - 0.04, f"{G.nodes[node]['winrate']}%", ha='center', va='center', fontsize=8, color='black', fontweight='bold')
            else:
                plt.text(x, y - 0.04, f"NA%", ha='center', va='center', fontsize=8, color='black', fontweight='bold')
        except Exception as e:
            print(e)
    while True:
        random_filename = generate_random_filename()
        if not os.path.exists("./static/charts/" + random_filename):
            plt.savefig("./static/charts/" + random_filename, dpi=1200)
            plt.close()
            break
    return jsonify({'plot_url': "/static/charts/" + random_filename})
@app.route("/community")
@limiter.exempt
def gotocomm():
    return render_template("community.html")

@app.route('/get_posts')
@limiter.exempt
def get_posts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, postcontent FROM posts")
    posts = [{"id": row[0], "username": row[1], "postcontent": row[2]} for row in cur.fetchall()]
    cur.close()
    return jsonify(posts)

@app.route('/add_post', methods=['POST'])
@limiter.limit("1/minute", override_defaults=False)
def add_post():
    data = request.get_json()
    username = data.get('username')
    postcontent = data.get('postcontent')
    if postcontent_exists(postcontent):
        return jsonify({"message": "Duplicate postcontent. Post not added."})
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO posts (username, postcontent) VALUES (%s, %s)", (username, postcontent))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Post added successfully"})
@app.route('/about')
@limiter.exempt
def gotoabt():
    return render_template("about.html")


def postcontent_exists(postcontent):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM posts WHERE postcontent = %s", (postcontent,))
    count = cur.fetchone()[0]
    cur.close()
    return count > 0
def user_exists(user):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user,))
    count = cur.fetchone()[0]
    cur.close()
    return count > 0
def ip_exists(ip):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE ip = %s", (ip,))
    count = cur.fetchone()[0]
    cur.close()
    return count > 0
@app.route("/lockname", methods=['GET'])
def lockinusername():
    username = request.args.get('usern')
    if user_exists(username) and username != None or ip_exists(get_client_ip() and username != None):
        return jsonify({"message": "choose another name or you have already chosen a name."})
    else:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, ip) VALUES (%s, %s)", (username, get_client_ip()))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "success"})


@app.route("/getname")
@limiter.exempt
def getname():
    if ip_exists(get_client_ip()):
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users WHERE ip = %s", (get_client_ip(),))
        username = cur.fetchone()[0]
        cur.close()
        return jsonify({"username": username})
    else:
        return jsonify({"username": ""})