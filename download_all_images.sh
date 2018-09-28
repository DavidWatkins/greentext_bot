while read p; do 
	./cli.js greentext top 1000 $p 
done < words.txt