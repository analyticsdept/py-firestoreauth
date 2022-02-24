from firestoreauth import FirestoreAuth

def create_new_user():
    try:
        with FirestoreAuth('__all') as ctx:
            ctx.create_user('rob', 'xxx')
    except Exception as e: print(str(e))

def login():
    print('logging in')
    try:
        with FirestoreAuth('__all', 'rob', 'xxx') as ctx:
            test('before')
            print("authenticated:", ctx.authenticated)
            test('after')
    except Exception as e: print(str(e))

def test(x):
    print(x)

# create_new_user()
login()