import os
import argparse
import csv

def visualize_results(path, k=5):
    results = {}

    with open(path, "r") as result_file:
        reader = csv.reader(result_file)
        next(reader)

        for row in reader:
            segment_signature_name, signature_name, distance = row
            segment_signature_name = segment_signature_name.rsplit('_', 2)[0]
            signature_name = signature_name.rsplit('.', 1)[0]
            results.setdefault(segment_signature_name, []).append((signature_name, float(distance)))

    results = {segment_signature_name: sorted(results, key=lambda x: x[1])[:k] for segment_signature_name, results in results.items()}

    correct = 0
    total = 0

    for segment_signature_name, topk in results.items():
        print(f"Most similar audio files for {segment_signature_name}:")
        if segment_signature_name == topk[0][0]:
            correct += 1
        total += 1

        for signature_name, distance in topk:
            print(f"{signature_name}: {distance}")
        print()

    print(f"Accuracy: {correct / total}")
    
def main():
    parser = argparse.ArgumentParser(description="Find the most similar audio file in a database.")
    parser.add_argument("path", type=str, help="Path to distance results file") 
    parser.add_argument("-k", "--k", type=int, default=5, help="Number of most similar audio files to display (default: 5)")
    args = parser.parse_args()
    
    visualize_results(args.path, args.k)

if __name__ == '__main__':
    main()