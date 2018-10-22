import time
import csv


movie_list = []
master_personnel_list = []
master_role_list = []


class Film:
    title = ""
    index = 0
    personnel_list = []
    role_list = []
    similarity_list = []
    bin_list = []
    year = 0

    def __init__(self, title, year, index, personnel_list):
        self.title = title
        self.index = index
        self.personnel_list = personnel_list
        self.year = year

    def setRoleList(self, role_list):
        self.role_list = role_list



def readInMoviesAndCreateMasterLists():

    with open('star_wars_test_scrape.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        people = True
        index = 0
        rowCount = 0

        for row in csv_reader:

            if people:
                movie_personnel = []
                movie_title = ""
                movie_year = ""


                #row 1 for movie
                for i in range(0, len(row)):
                    if i == 0:  # movie title
                        movie_title = row[i].replace("{", ",")
                        print(movie_title)
                    elif i == 1:  # movie year made
                        movie_year = row[i]
                        print(movie_year)
                    else:  # personnel
                        if row[i] != '':
                            movie_personnel.append(row[i])
                            print(row[i])

                            #add to master list if person isn't there in that role



                curr_film = Film(movie_title, movie_year, index, movie_personnel)
                movie_list.append(curr_film)
                people = False

            else:
                movie_roles = []

                for i in range(2, len(row)):  # skips title and year, straight to roles
                    if row[i] != '':
                        movie_roles.append(row[i])

                        # if person isn't already in master list in specific role just read in, add both to master
                        indices = [p for p, x in enumerate(master_personnel_list) if x == movie_personnel[i-2]]
                        append = True
                        for k in indices:
                            if master_role_list[k] == row[i]:
                                append = False

                        if append:
                            master_personnel_list.append(movie_personnel[i-2])  # add to master list if not already there
                            master_role_list.append(row[i])
                            print(str(index) + "th movie, master list length: " + str(len(master_personnel_list)))

                if len(movie_roles) != len(movie_personnel):
                    raise Exception('mismatch: ' + index)
                movie_list[index].setRoleList(movie_roles)
                people = True

                # print movie info to screen
                # print(str(index) + " " + movie_list[index].title + " " + str(movie_list[index].year))
                # print(movie_list[index].role_list)
                # print(movie_list[index].personnel_list)

                index += 1

            rowCount += 1
            if rowCount >= 24:
                break


def createAndWriteBinLists():

    #  write in headers for file (contents of master personnel/role lists)
    with open("star_wars_bin_test.csv", "a", newline="") as f:

        f.write('X,X,')
        for role in master_role_list:
            f.write(role + ',')
        f.write('\n')

        f.write('X,X,')
        for person in master_personnel_list:
            f.write(person + ',')
        f.write('\n')

        total_num_personnel = len(master_personnel_list)

        for movie in movie_list:
            print(movie.title)
            bin_list = [0] * total_num_personnel
            for i in range(0, len(movie.personnel_list)):
                name = movie.personnel_list[i]
                role = movie.role_list[i]

                indices = [ind for ind, x in enumerate(master_personnel_list) if x == name]
                for k in indices:
                    if role == master_role_list[k]:
                        bin_list[k] = 1

            f.write(movie.title + ',')
            f.write(movie.year + ',')
            for element in bin_list:
                f.write(str(element) + ',')
            f.write('\n')


start = time.time()

readInMoviesAndCreateMasterLists()
createAndWriteBinLists()

end = time.time()
print("runtime: " + str(round(end-start)) + " seconds")
