import sqlite3
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Connect to database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()
print(Fore.CYAN + "Database connected successfully!" + Style.RESET_ALL)

# Create tables with UNIQUE constraints
cursor.execute('''
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    author_id INTEGER,
    genre_id INTEGER,
    publication_year INTEGER,
    status TEXT DEFAULT 'Unread',
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
)
''')
conn.commit()
print(Fore.CYAN + "Tables created successfully!" + Style.RESET_ALL)

# Function to get or insert author ID
def get_or_insert_author(name):
    name = name.strip().title()
    cursor.execute('SELECT author_id FROM authors WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute('INSERT INTO authors (name) VALUES (?)', (name,))
    conn.commit()
    return cursor.lastrowid

# Function to get or insert genre ID
def get_or_insert_genre(name):
    name = name.strip().title()
    cursor.execute('SELECT genre_id FROM genres WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute('INSERT INTO genres (name) VALUES (?)', (name,))
    conn.commit()
    return cursor.lastrowid

# Insert initial data
authors = [
    'George Orwell', 'Nora Sakavic', 'John Green', 'R.J. Palacio', 'Leigh Bardugo',
    'Alyona Philipenko', 'Tillie Cole', 'Bodo Schäfer', 'William Golding', 'J.K. Rowling',
    'Toni Morrison', 'Neil Gaiman', 'Jane Austen', 'Suzanne Collins', 'Octavia E. Butler',
    'Ray Bradbury', 'Holly Black', 'Chimamanda Ngozi Adichie', 'Kazuo Ishiguro', 'Erin Morgenstern'
]
genres = [
    'Dystopian', 'Young Adult', 'Middle Grade', 'Fantasy', 'Romance',
    'Personal Finance', 'Classic', 'Science Fiction', 'Literary Fiction', 'Historical Fiction'
]

author_ids = {name: get_or_insert_author(name) for name in authors}
genre_ids = {name: get_or_insert_genre(name) for name in genres}

books = [
    ('1984', author_ids['George Orwell'], genre_ids['Dystopian'], 1949, 'Unread'),
    ('The Foxhole Court', author_ids['Nora Sakavic'], genre_ids['Young Adult'], 2013, 'Unread'),
    ('Looking for Alaska', author_ids['John Green'], genre_ids['Young Adult'], 2005, 'Unread'),
    ('Wonder', author_ids['R.J. Palacio'], genre_ids['Middle Grade'], 2012, 'Unread'),
    ('Shadow and Bone', author_ids['Leigh Bardugo'], genre_ids['Fantasy'], 2012, 'Unread'),
    ('Siege and Storm', author_ids['Leigh Bardugo'], genre_ids['Fantasy'], 2013, 'Unread'),
    ('Ruin and Rising', author_ids['Leigh Bardugo'], genre_ids['Fantasy'], 2014, 'Unread'),
    ('The Odd One in His Game', author_ids['Alyona Philipenko'], genre_ids['Young Adult'], 2020, 'Unread'),
    ('A Thousand Boy Kisses', author_ids['Tillie Cole'], genre_ids['Romance'], 2016, 'Unread'),
    ('A Dog Called Money', author_ids['Bodo Schäfer'], genre_ids['Personal Finance'], 2000, 'Unread'),
    ('Lord of the Flies', author_ids['William Golding'], genre_ids['Classic'], 1954, 'Unread'),
    ('Harry Potter and the Sorcerer\'s Stone', author_ids['J.K. Rowling'], genre_ids['Fantasy'], 1997, 'Unread'),
    ('Beloved', author_ids['Toni Morrison'], genre_ids['Literary Fiction'], 1987, 'Unread'),
    ('Good Omens', author_ids['Neil Gaiman'], genre_ids['Fantasy'], 1990, 'Unread'),
    ('Pride and Prejudice', author_ids['Jane Austen'], genre_ids['Classic'], 1813, 'Unread'),
    ('The Hunger Games', author_ids['Suzanne Collins'], genre_ids['Dystopian'], 2008, 'Unread'),
    ('Fahrenheit 451', author_ids['Ray Bradbury'], genre_ids['Dystopian'], 1953, 'Unread'),
    ('The Cruel Prince', author_ids['Holly Black'], genre_ids['Fantasy'], 2018, 'Unread'),
    ('The Night Circus', author_ids['Erin Morgenstern'], genre_ids['Fantasy'], 2011, 'Unread')
]

# Insert books with error handling
for book in books:
    try:
        cursor.execute('INSERT INTO books (title, author_id, genre_id, publication_year, status) VALUES (?, ?, ?, ?, ?)', book)
    except sqlite3.IntegrityError:
        print(Fore.YELLOW + f"Skipped duplicate book: {book[0]}" + Style.RESET_ALL)
conn.commit()
print(Fore.CYAN + "Books inserted successfully!" + Style.RESET_ALL)

# Check for duplicates
cursor.execute("SELECT title, COUNT(*) as count FROM books GROUP BY title HAVING count > 1")
duplicates = cursor.fetchall()
if duplicates:
    print(Fore.RED + "Duplicates found in database:" + Style.RESET_ALL)
    print(tabulate(duplicates, headers=['Title', 'Count'], tablefmt='grid'))
else:
    print(Fore.GREEN + "No duplicates in database." + Style.RESET_ALL)

# Interactive menu
while True:
    print(Fore.CYAN + "\n=== Personal Library Management System ===" + Style.RESET_ALL)
    print("1. List books by genre")
    print("2. List books by author")
    print("3. Mark book as read")
    print("4. Count books per author")
    print("5. Add a new book")
    print("6. Delete a book")
    print("7. Export library to CSV")
    print("8. List all books")
    print("9. Exit")
    choice = input("Enter choice (1-9): ").strip()

    if choice == '1':
        genre = input("Enter genre (e.g., Dystopian, Young Adult, Fantasy): ").strip().title()
        cursor.execute("SELECT books.title, authors.name, books.publication_year, books.status, genres.name FROM books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id WHERE genres.name = ? ORDER BY books.publication_year DESC", (genre,))
        books = cursor.fetchall()
        if books:
            print(f"\n{Fore.CYAN}{genre} Books:{Style.RESET_ALL}")
            print(tabulate(books, headers=['Title', 'Author', 'Year', 'Status', 'Genre'], tablefmt='fancy_grid'))
        else:
            print(Fore.RED + "No books found for this genre." + Style.RESET_ALL)
    elif choice == '2':
        author = input("Enter author name (e.g., Leigh Bardugo): ").strip().title()
        cursor.execute("SELECT books.title, authors.name, books.publication_year, books.status, genres.name FROM books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id WHERE authors.name = ? ORDER BY books.publication_year DESC", (author,))
        books = cursor.fetchall()
        if books:
            print(f"\n{Fore.CYAN}Books by {author}:{Style.RESET_ALL}")
            print(tabulate(books, headers=['Title', 'Author', 'Year', 'Status', 'Genre'], tablefmt='fancy_grid'))
        else:
            print(Fore.RED + f"No books found for author '{author}'." + Style.RESET_ALL)
    elif choice == '3':
        title = input("Enter book title to mark as read: ").strip()
        cursor.execute("SELECT title FROM books WHERE title = ?", (title,))
        if cursor.fetchone():
            cursor.execute("UPDATE books SET status = 'Read' WHERE title = ?", (title,))
            conn.commit()
            print(Fore.GREEN + f"'{title}' marked as read!" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Book '{title}' not found." + Style.RESET_ALL)
    elif choice == '4':
        cursor.execute("SELECT authors.name, COUNT(books.book_id) FROM books JOIN authors ON books.author_id = authors.author_id GROUP BY authors.name ORDER BY authors.name")
        counts = cursor.fetchall()
        print(f"\n{Fore.CYAN}Books per Author:{Style.RESET_ALL}")
        print(tabulate(counts, headers=['Author', 'Book Count'], tablefmt='fancy_grid'))
    elif choice == '5':
        title = input("Enter book title: ").strip()
        author = input("Enter author name: ").strip().title()
        genre = input("Enter genre: ").strip().title()
        year = input("Enter publication year (e.g., 2023): ").strip()
        status = input("Enter status (e.g., Unread, Reading, Read): ").strip()
        try:
            year = int(year)
        except ValueError:
            print(Fore.RED + "Invalid year! Please enter a number." + Style.RESET_ALL)
            continue
        author_id = get_or_insert_author(author)
        genre_id = get_or_insert_genre(genre)
        try:
            cursor.execute('INSERT INTO books (title, author_id, genre_id, publication_year, status) VALUES (?, ?, ?, ?, ?)', 
                          (title, author_id, genre_id, year, status))
            conn.commit()
            print(Fore.GREEN + f"Book '{title}' added successfully!" + Style.RESET_ALL)
        except sqlite3.IntegrityError:
            print(Fore.RED + f"Book '{title}' already exists." + Style.RESET_ALL)
    elif choice == '6':
        title = input("Enter book title to delete: ").strip()
        cursor.execute("SELECT title FROM books WHERE title = ?", (title,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM books WHERE title = ?", (title,))
            conn.commit()
            print(Fore.GREEN + f"Book '{title}' deleted successfully!" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Book '{title}' not found." + Style.RESET_ALL)
    elif choice == '7':
        import csv
        cursor.execute("SELECT books.title, authors.name, books.publication_year, books.status, genres.name FROM books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id ORDER BY books.title")
        books = cursor.fetchall()
        with open('books.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Author', 'Year', 'Status', 'Genre'])
            writer.writerows(books)
        print(Fore.GREEN + "Library exported to books.csv!" + Style.RESET_ALL)
    elif choice == '8':
        cursor.execute("SELECT books.title, authors.name, books.publication_year, books.status, genres.name FROM books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id ORDER BY books.title")
        books = cursor.fetchall()
        if books:
            print(f"\n{Fore.CYAN}All Books:{Style.RESET_ALL}")
            print(tabulate(books, headers=['Title', 'Author', 'Year', 'Status', 'Genre'], tablefmt='fancy_grid'))
        else:
            print(Fore.RED + "No books in the library." + Style.RESET_ALL)
    elif choice == '9':
        break
    else:
        print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

conn.close()
print(Fore.CYAN + "Database connection closed." + Style.RESET_ALL)               




        
      

    