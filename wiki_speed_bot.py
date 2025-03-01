from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
import requests
from datetime import datetime

def get_target_feature(url):
    # Filter common non useful words
    cnu = ['but', 'how', 'the', 'of', 'or', 'who', 'not', 'and', 'a', 'to', 'is', 'a', 'in', 'i', 'for', 'with', 'on', 'from', 'by', 'be']

    # Words vector
    words = []
    # Global feature vector
    feature_vector = []

    html = urlopen(url).read()
    soup = bs(html, "html.parser")

    for script in soup(["script", "style"]):
        script.decompose()
    strips = list(soup.stripped_strings)

    for s in strips:
        ss = list(s.split(' '))
        for word in ss:
            word = word.lower()
            if word.isalnum() and len(word) > 1 and not word.isdigit():
                add = True
                for f in cnu:
                    if f in word:
                        add = False
                if add:
                    words.append(word)

    # Vocabulary
    vocab = list(set(words))

    # Create feature vector
    for word in vocab:
        c = words.count(word)
        feature_vector.append((word, c))

    feature_vector.sort(key=lambda x:x[1], reverse=True)

    return feature_vector, vocab, words

def calc_prob(target_vector, target_vocab, url, best_score):
    _, _, words = get_target_feature(url)
    prob = 0
    cost_of_neg = 10 #round(0.1 * len(target_vector))
    for i in range(len(target_vector)):
        word, count = target_vector[i]
        ct = words.count(word)
        prob += abs(count - ct)

        # if prob is bigger than best score, then move on
        if prob > best_score:
            return 99999

        #if ct == 0:
            #prob += 1 #cost_of_neg * abs(count-ct)
        #else:
        #    prob += abs(count-ct)

    return prob


def get_wiki_sites(site):
    res = requests.get(site)
    soup = bs(res.text, "html.parser")
    links = []

    filter = ['File', '.png', 'http://', 'https://', 'ISBN', '%', 'Talk:', 'Portal:', 'Special:', 'Help:', 'Category:',
              'Main_Page', 'Wikipedia:', '(identifier)', 'Terms_of_Use', 'Privacy_policy', 'Cookie_statement', '#', '(',
              'Template:']

    for link in soup.find_all("a"):
        url = link.get("href", "")
        if "/wiki/" in url:
            add_wiki = True
            for word in filter:
                if word in url:
                    add_wiki = False
            if add_wiki:
                links.append(url)

    return list(set(links))  # Remove duplicates


def wiki_speed_run_bot():
    # Start site
    start_site = 'https://en.wikipedia.org/wiki/Bundle_adjustment'
    # Target site
    target_site = 'https://en.wikipedia.org/wiki/Ambient_occlusion'

    # Start links
    links = get_wiki_sites(start_site)
    # Sites that have already been visited, avoid cycles
    Visited_sites = []
    # Sites to be visited
    queue_sites = links

    while queue_sites:
        site = queue_sites[0]
        print("Searching site: " + site)
        print("VS: " + str(len(Visited_sites)) + ", queue_sites: " + str(len(queue_sites)))

        Visited_sites.append(site)
        links = get_wiki_sites('https://en.wikipedia.org' + site)

        for link in links:
            if link not in Visited_sites:
                queue_sites.append(link)

        if 'https://en.wikipedia.org' + site == target_site:
            print("Found site: " + target_site)
            break

        queue_sites.pop(0)

    for link in Visited_sites:
        print(link)






start_time = datetime.now()

# Start site
start_site = '/wiki/Stranger_Things'
# Target site
target_site = '/wiki/Non-fungible_token'


feature_vector, vocab, _ = get_target_feature('https://en.wikipedia.org' + target_site)
print(vocab)
print(feature_vector)

search = True

best_site = start_site
hist_sites = []
while(search):
    links = get_wiki_sites('https://en.wikipedia.org' + best_site)
    prob_links = []

    index = 0
    link_size = len(links)

    print("Found " + str(len(links)) + " links from " + str(best_site))
    for link in links:
        if link == target_site:
            print("Found site: " + str(link))
            time_elapsed = datetime.now() - start_time
            search = False

    if search:
        best_score = 9999
        for link in links:
            index += 1

            if hist_sites.count(link) == 0:
                # Calculate probabilities for each link
                p = calc_prob(feature_vector, vocab, 'https://en.wikipedia.org' + link, best_score)
                #prob_links.append((link, p))

                if p < best_score:
                    best_score = p
                    best_site = link

                print("   - [ " + str(index) + " / " + str(link_size) + " ] Searching: " + str(link) + " [" + str(p) +"]")

        # Sort list by probabilities
        #prob_links.sort(key=lambda x:x[1])

        # Pick best probable site
        #for i in range(len(prob_links)):
        #    c = hist_sites.count(prob_links[i][0])
            #print((prob_links[i][0], c))
        #    if c == 0:
        #        best_site = prob_links[i][0]
        #        break

        hist_sites.append(best_site)

        print(best_site)



print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
print(hist_sites)
















