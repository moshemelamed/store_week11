from bottle import route, run, template, static_file, get, post, delete, request
from sys import argv
import json
import pymysql


connection =pymysql.connect(host='localhost',
                            user="root",
                            password='momo',
                            db='store',
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)


@get("/")
def index():
    return template("index.html")


@get("/admin")
def admin_portal():
    return template("pages/admin.html")


@post('/category')
def add_category():
    count=0
    going_out = {}
    name = request.forms.get("name")
    if name == " ":
        return json.dumps({"STATUS": "ERROR", "MSG": "Bad request", "CAT_ID": None, "CODE": 400})

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM category"
            cursor.execute(sql)
            result = cursor.fetchall()
            for res in result:
                count = count + 1
                print(res['category_name'])
                if name == res['category_name']:
                    going_out["CODE"] = 200
                    going_out["STATUS"] = "ERROR"
                    going_out["MSG"] = "'{}' already exists".format(name)
                    going_out["CAT_ID"] = None
                    return json.dumps(going_out)
                elif count >= len(result) and res['category_name'] != name:
                    sql = "INSERT INTO `category`(`category_name`)VALUES ('{}')".format(name)
                    cursor.execute(sql)
                    connection.commit()
                    going_out["CODE"] = 201
                    going_out["STATUS"] = "SUCCESS"
                    going_out["MSG"] = "category created successfully"
                    going_out["CAT_ID"] = res['category_id']
                    return json.dumps(going_out)
    except:
        return json.dumps({"STATUS":"ERROR", "MSG":"Internal error", "CAT_ID":None, "CODE":500})


@route("/category/<catId>", method='DELETE')
def delete_category(catId):
    try:
        with connection.cursor() as cursor:
            sql = ('DELETE FROM category WHERE category_id = {}'.format(catId))
            cursor.execute(sql)
            connection.commit()
            return json.dumps({'STATUS': 'SUCCESS', 'MSG': 'The category was deleted successfully'})

    except:
        return json.dumps({'STATUS': 'ERROR', 'MSG': "Internal error"})

@get("/categories")
def load_categories():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM category"
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({'STATUS' : 'SUCCESS', 'CATEGORIES':result})
    except:
        return json.dumps({'STATUS' : 'ERROR', 'MSG': "Internal error"})


@route('/product/<pid>', method='DELETE')
def delete_product(pid):
    try:
        with connection.cursor() as cursor:
            sql = ('DELETE FROM products WHERE id = {}'.format(pid))
            cursor.execute(sql)
            connection.commit()
            return json.dumps({'STATUS':'SUCCES', 'MSG':'The product was deleted successfully'})
    except:
        return json.dumps({'STATUS' : 'ERROR', 'MSG': "Internal error"})

@get("/products")
def load_products():
    try:
        with connection.cursor() as cursor:
            sql = ('SELECT category, description, price, title, favorite, img_url, id FROM products ')
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({'STATUS':'SUCCESS','PRODUCTS': result})
    except:
        return json.dumps({'STATUS' : 'ERROR', 'MSG': "Internal error"})


@get("/product/<pid>")
def load_products(pid):
    try:
        with connection.cursor() as cursor:
            sql = ('SELECT category, description, price, title, favorite, img_url, id FROM products')
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({'STATUS':'SUCCESS','PRODUCTS': result})
    except:
        return json.dumps({'STATUS' : 'ERROR', 'MSG': "Internal error"})



@get('/category/<id>/products')
def list_products_cat(id):
    try:
        with connection.cursor() as cursor:
            sql = ('SELECT category, description, price, title, favorite, img_url, id FROM products WHERE category = {} ORDER BY favorite DESC, creation_date ASC'.format(id) )
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({'STATUS':'SUCCESS','PRODUCTS': result})
    except:
        return json.dumps({'STATUS':'ERROR', 'MSG': "Internal error"})


@post("/product")
def add_product():

    cat_id = request.POST.get('id')
    category = request.POST.get('category')
    title = request.POST.get('title')
    description = request.POST.get('desc')
    price = request.POST.get('price')
    favorite = request.POST.get('favorite')
    if favorite == None:
        n_fav = 0
    else:
        n_fav = 1
    img_url = request.POST.get('img_url')
    if cat_id != '':
        try:
            with connection.cursor() as cursor:
                sql = ('UPDATE products SET category=%s, title=%s, description=%s, price=%s, favorite=%s, img_url=%s WHERE id=%s')
                data = (category,str(title),str(description),price,n_fav,str(img_url), id)
                cursor.execute(sql, data)
                connection.commit()
                return json.dumps({'STATUS':'SUCCESS', 'MSG':'The product was added/updated successfully'})
        except:
            return json.dumps({'STATUS':'ERROR', 'MSG':"error in the updating"})
    else:
        try:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO products VALUES(id,%s,%s,%s,%s,%s,%s,now())'
                data = (category,title,description,price,n_fav,img_url)
                cursor.execute(sql, data)
                connection.commit()
        except:
            return json.dumps({'STATUS':'ERROR', 'MSG':"error in the values adding"})



@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


# run(host='0.0.0.0', port=argv[1])
def main():
    run(host='localhost', port=7001)


if __name__ == '__main__':
    main()
