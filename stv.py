from typing import List
import time
from copy import deepcopy
from itertools import permutations
from tqdm import tqdm
import json
from typing import Union

FILENAME = '00016-00000001.toi'

class STV:
    def __init__(self, filename=FILENAME) -> None:

        # Store the unique voters' ballots
        # [index, linear order]
        self.unique_ballots_original: List[List[int]] = []
        
        # Store the number of voters with the same ballots
        # [index, count of identical ballots]
        self.counts_ballots: List[int] = []

        # The list of currently available alternatives. Known to be 11 in the beginning
        self.alternatives: List[int] = list(range(1,12))

        # Define all possible ballots (exclude 10 and 11 since they appear very rarely)
        self.relevant_alternatives: List[int] = [1,2,3,4,5,6,7,8,9]
        self.relevant_alternatives_permutations: List[List[int]] = list(permutations(self.relevant_alternatives))

        with open(filename) as f:
            for line in f:

                # Skip uninformative lines
                if line.startswith('#'):
                    continue
                
                # Extract the ballot and how often it repeats in the profile
                count, ballot = line.split(':')

                # Append the ballot and the counts to the lists
                self.unique_ballots_original.append([int(x) for x in ballot.replace('}', '').replace('{', '').split(',')])
                self.counts_ballots.append(int(count))
        self.reset()
        
    def reset(self) -> None:
        """Reset the ballots to the original ones"""
        self.unique_ballots = deepcopy(self.unique_ballots_original)

    def sigma(self) -> None:
        """Single application of the sigma function"""

        # Extract each voter's top choice
        top_choices = [ballot[0] for ballot in self.unique_ballots]
        
        # Find the plurality scores for each top choice
        frequencies = {}
        for choice, count in zip(top_choices, self.counts_ballots):
            if choice not in frequencies:
                frequencies[choice] = 0
            frequencies[choice] += count

        # Case where there are alternatives with a plurality score of 0
        alternatives_to_remove = []
        zero_votes = False
        for alternative in self.alternatives:
            if alternative not in frequencies:
                alternatives_to_remove.append(alternative)
                zero_votes = True

        # Get the alternatives with the smallest plurality score 
        if not zero_votes:
            min_votes = min(frequencies.values())
            alternatives_to_remove = [x for x in frequencies if frequencies[x] == min_votes]
        
        # Remove those alternatives from each ballot
        for alternative in alternatives_to_remove:
            self.alternatives.remove(alternative)
            for ballot in self.unique_ballots:
                if alternative in ballot: ballot.remove(alternative)
        self.unique_ballots, self.counts_ballots = (
            zip(*[(ballot, count) for ballot, count in zip(self.unique_ballots, self.counts_ballots) if ballot])
        )

    def elect(self) -> Union[List[int], int]:
        while True:
            
            # Single winner is found!
            if len(self.alternatives) == 1:
                return self.alternatives[0]

            # Sigma function application
            last = self.alternatives.copy()
            self.sigma()
            
            # There is a tie
            if self.alternatives == []:
                return last
    
    def manipulate(self, x: int) -> None:
        elections = {}

        # Try all possible linear orders
        for permutation in self.relevant_alternatives_permutations:
            
            # For each agent, if the agent prefers 'x' over '8', replace its preference with the current permutation
            for i, ballot in enumerate(self.unique_ballots):
                if x in ballot:
                    if 8 in ballot:
                        if ballot.index(x) < ballot.index(8):
                            self.unique_ballots[i] = list(permutation)
                    else:
                        self.unique_ballots[i] = list(permutation)

            # Elect a winner and record it
            output = self.elect()
            if output not in elections: elections[output] = 0
            elections[output] += 1

            # Reset the election, so the voters come back to their true preferences
            self.reset()
        
        return elections


if __name__ == '__main__':
    start_time = time.time()
    stv = STV()
    # print('*' * 50)
    # print('NUMBER OF AGENTS THAT PREFER AN ALTERNATIVE OVER 8')
    # for alternative in stv.alternatives:
    #     count = 0
    #     for ballot in stv.unique_ballots:
    #         if alternative in ballot:
    #             count += 8 not in ballot or ballot.index(alternative) < (ballot.index(8)-1)
    #     print(alternative, count)
    # print('*' * 50)
    # print('NUMBER OF AGENTS THAT PREFER 8 OVER THE OTHER ALTERNATIVE')
    # for alternative in stv.alternatives:
    #     count = 0
    #     for ballot in stv.unique_ballots:
    #             count += 8 in ballot and (alternative not in ballot or ballot.index(8) < ballot.index(alternative))
    #     print(alternative, count)
    # print('*' * 50)
    results = {}
    for i in tqdm(stv.relevant_alternatives):
        if i == 8: continue
        results[i] = stv.manipulate(i)
    print(results)

    # winner = stv.elect()
    # print(f'Winner: {winner}')
    print(time.time() - start_time)

# Since 8 is the Condorcet Winner, agents with different preferences should combine their forces.
# So for example, find the agents that prefer both x and y over 8, and let them all choose x over 8.
# That way the powers of groups 2 > 8 and 2 > 3 can combine
