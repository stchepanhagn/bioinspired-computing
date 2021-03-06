import user as u
import movieDB as mdb
import random
import json
from operator import itemgetter, attrgetter, methodcaller

# not used yet
dList = []

STIMULATION_RATIO = 0.5
SUPPRESION_RATIO = 0.3
DEATH_RATIO = 0.1
NEIGHBOURS_MAX = 10
MAX_RECOMENDATIONS = 5


def main():
    mdb.loadDB(mdb.FIXDB)
    # users = generateRandomUsers(1500,150)
    users = load('users.txt')
    # save(users, 'users.txt')
    # executeAIS(users[0],users[1:])
    # neighbours = findNeighbors(users, users[8], 10)
    print users[8].biasList
    neighbours = executeAIS(users[8], users)
    print neighbours
    recomendMovies(users[8], neighbours)
    print users[8].biasList


def load(file):
    f = open(file, 'r')
    users = []
    for line in f:
        jsonUser = json.loads(line)
        user = u.User(jsonUser['name'], jsonUser['biasList'])
        user.movieRatings = jsonUser['movieRatings']
        users.append(user)
    print 'User database loaded!'
    f.close()
    return users


def save(users, file):
    f = open(file, 'w')
    for user in users:
        x = json.dumps(user, default=lambda o: o.__dict__)
        f.write(x)
        f.write("\n")
    f.close()
    print 'Saved!'


def recomendMovies(user, neighbors):
    notWatchedFrequency = dict()
    notWatchedScore = dict()
    uMovieList = user.getMovieList()
    for neighbor in neighbors:
        for movieRating in neighbor[0].movieRatings:
            if movieRating[0] not in uMovieList:
                movieTitle = movieRating[0]['Title']
                if (notWatchedScore.has_key(movieTitle)):
                    notWatchedFrequency[movieTitle] = notWatchedFrequency[movieTitle] + 1
                    notWatchedScore[movieTitle] = notWatchedScore[movieTitle] + movieRating[1]
                else:
                    notWatchedFrequency[movieTitle] = 1
                    notWatchedScore[movieTitle] = movieRating[1]

    normalizedScore = dict()
    for key in notWatchedFrequency.keys():
        normalizedScore[key] = notWatchedScore[key] / notWatchedFrequency[key]

    sortedMap = mdb.returnOrderedMap(normalizedScore)
    i = 0
    for k, v in sortedMap:
        print k, v
        i += 1
        if i == MAX_RECOMENDATIONS:
            break


def executeAIS(antigen, users):
    neighbors = list(users)
    neighbors.remove(antigen)
    stable = 0
    antibodies = []
    iterations = 0;
    while stable < 10:
        index = random.randrange(len(neighbors))
        newAntibody = neighbors.pop(index)
        antibodies.append(newAntibody)
        stable = 0
        iterations += 1
        while (stable < 10) & (NEIGHBOURS_MAX <= len(antibodies)):
            removeList = []
            for antibody in antibodies:
                agStimulation = STIMULATION_RATIO * abs(compare(antigen, antibody)) * antigen.concentration * antibody.concentration
                deathRate = DEATH_RATIO * antibody.concentration
                abSupression = 0
                for antibody2 in antibodies:
                    if antibody2 == antibody:
                        continue
                    abSupression = abSupression + (abs(compare(antibody, antibody2)) * antibody.concentration * antibody2.concentration)
                abSupression = (SUPPRESION_RATIO / len(antibodies)) * abSupression
                antibody.concentration = agStimulation + abSupression - deathRate
                if antibody.concentration < 23:
                    removeList.append(antibody)
            for rm in removeList:
                antibodies.remove(rm)
            stable += 1
            print 'Stable', stable, 'remove:', len(removeList)

    antiList = []
    for antibody in antibodies:
        antiList.append([antibody, compare(antibody, antigen)])
    print 'Users left:',len(neighbors)
    return antiList


# find k closest neighbors for mainUser in the list users
def findNeighbors(users, mainUser, k):
    distances = []
    for user in users:
        if user == mainUser: continue
        distances.append([user, [compare(mainUser, user)]])
    distances = sorted(distances, key=itemgetter(1))
    # distances = distances[::-1]
    neighbors = []
    for i in range(k):
        neighbors.append(distances.pop())
    return neighbors


# print distances


# generate random biased users
def generateRandomUsers(nUsers, nMovies):
    generatedUsers = []
    user = None
    for i in range(nUsers):
        user = u.User(str(i), generateRandomGenreBias(user, 5))
        copy = list(mdb.movies)
        for j in range(nMovies):
            index = random.randint(0, len(copy) - 1)
            movie = copy.pop(index)
            score = biasScore(user, movie)
            user.movieRatings.append((movie, score))
        generatedUsers.append(user)
    return generatedUsers


# Give a score to a movie based on user genre bias
def biasScore(user, movie):
    genreString = movie['Genre']
    movieGenres = genreString.split(',')
    biasList = user.biasList
    score = 0;
    biasValue = 0;
    for i in range(len(biasList)):
        bias = biasList[i][0]
        for genre in movieGenres:
            genre = genre.strip()
            if bias == genre:
                biasValue = biasList[i][1]
                break;
    if biasValue == 0:
        return random.randint(0, 8)
    score = random.randint(1, (10 - biasValue)) + biasValue
    return score


# generate genre bias for an user
def generateRandomGenreBias(user, n):
    genreList = list(mdb.getGenreList())
    biasList = []
    for i in range(n):
        genre = genreList.pop(random.randrange(len(genreList)))
        biasList.append((genre, n - i))
    return biasList


# calculate how much an user likes each genre based on ratings
def calculateGenreRate(user):
    genreOccurence = dict(mdb.countGenres(user.getMovieList()))
    genreMap = dict()
    for mt in user.movieRatings:
        movie = mt[0]
        genreString = movie['Genre']
        genres = genreString.split(',')
        for genre in genres:
            genre = genre.strip()
            if (genreMap.has_key(genre)):
                genreMap[genre] = genreMap[genre] + mt[1]
            else:
                genreMap[genre] = mt[1]
    genreRatio = dict()
    for gen in genreMap.keys():
        genreRatio[gen] = genreMap[gen] / (genreOccurence[gen] * len(user.movieRatings))
    return genreRatio


# function used to calculate correlation metric between two users
# only using one pearson correlation so far
def compare(user1, user2):
    u1GenreRate = calculateGenreRate(user1)
    u2GenreRate = calculateGenreRate(user2)
    overlappedGenres = []
    for genre1 in u1GenreRate.keys():
        if genre1 in u2GenreRate.keys():
            overlappedGenres.append(genre1)
    sum1 = 0.0
    for genre in overlappedGenres:
        sum1 += ((u1GenreRate[genre] - averageOfVector(u1GenreRate.values())) * (
        u2GenreRate[genre] - averageOfVector(u2GenreRate.values())))
    sum2 = 0.0
    for genre in overlappedGenres:
        sum2 += pow(((u1GenreRate[genre] - averageOfVector(u1GenreRate.values()))), 2)
    sum3 = 0.0
    for genre in overlappedGenres:
        sum3 += pow(((u2GenreRate[genre] - averageOfVector(u2GenreRate.values()))), 2)
    pearson = sum1 / pow((sum3 * sum2), 0.5)

    # second pearson
    u1MovieMap = user1.getMovieMap()
    u2MovieMap = user2.getMovieMap()
    overlappedMovies = []
    for movie1 in u1MovieMap.keys():
        if movie1 in u2MovieMap.keys():
            overlappedMovies.append(movie1)
    sum1 = 0.0
    for movie in overlappedMovies:
        sum1 += ((u1MovieMap[movie] - averageOfVector(u1MovieMap.values())) * (
        u2MovieMap[movie] - averageOfVector(u2MovieMap.values())))
    sum2 = 0.0
    for movie in overlappedMovies:
        sum2 += pow(((u1MovieMap[movie] - averageOfVector(u1MovieMap.values()))), 2)
    sum3 = 0.0
    for movie in overlappedMovies:
        sum3 += pow(((u2MovieMap[movie] - averageOfVector(u2MovieMap.values()))), 2)
    pearson2 = sum1 / pow((sum3 * sum2), 0.5)

    return (pearson2 * 0.8 + pearson * 0.2)


# calculate the average value of a vector
def averageOfVector(vector):
    avg = 0
    for x in vector:
        avg = avg + x
    return avg / len(vector)


main()
