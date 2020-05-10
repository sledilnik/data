#!/usr/bin/perl -w

use strict;
use URI;
use HTTP::Request::Common qw(POST);
use LWP::UserAgent;
use Data::Dumper;

my $url = 'https://www.policija.si/medijsko-sredisce/dogodki-v-zadnjih-24-urah';
my %stats; 

# headers
print join("\t", 'day', 'month', 'year', 'url', 'title', 'calls', 'interventions', 'road', 'peace', 'felonies', 'breaks', 'damage', 'steals', 'robberies', 'violence', 'threat', 'deaths', 'text')."\n";
#foreach my $year (2020 .. 2001) {
for (my $year = 2020; $year >= 2001; $year--) {
	for (my $month = 12; $month > 0; $month--) {
#	foreach my $month (12 .. 1) {
# scrape
		if (!-f "./index/$year-$month.html") {
			my $ua = LWP::UserAgent->new;
			my $result = $ua->request(POST $url, [
			  leto  => $year,
			  mesec => $month,
			  show  => 'yes',
			  submit => 'Submit',
			]);
			my $index = $result->as_string;
			open (OUT, ">./index/$year-$month.html");
			print OUT $index;
			close OUT;
			sleep 1;
		}		

# parse
		my $file = readpipe ("cat ./index/$year-$month.html");
		my @articles = split/<div class='article'>/s ,$file;
		foreach my $article (@articles) {
			if ($article =~ /<span class='day'>(\d+)\..*?<span class='month'>(\w+)\.?.*?<span class='year'>(\d+)<.*?<div class='datetext'>(.*?)<\/div>/s) {	#'
				my $d = $1;
				my $m = $2;
				my $y = $3;	
				my $body = $4;

				$body =~ s/&nbsp;//g;
				my $url = my $title = my $text = "";
				$url = $1 if ($body =~ /<a href='(.*?)'>/gs);
				$title = $1 if ($body =~ /<h4>(.*?)<\/h4>/gs);
					$title =~ s/\s+$//g;
				$text = $1 if ($body =~ /<p>(.*?)<\/p>/gs);

# before 4/13/2011 there were no summaries, so download them
				if (!$text and $title =~ /pregled/i and $year <= 2011) {
	# if no body, fetch url
					if (!-f "./deep/$y-$month-$d.html") {
						system("wget -O ./deep/$y-$month-$d.html https://www.policija.si$url");
						sleep 1;
					}
					my $deep = readpipe("cat ./deep/$y-$month-$d.html");
					if ($deep =~ /<div itemprop="articleBody">(.*?)<\/div>/sg) {
						$text = $1;
						$text =~ s/<br>//sg;
					}
				}

# collect data points
				$text =~ s/\t/ /g;
				$text =~ s/&scaron;/š/g;
				$text =~ s/\ben[ao]\b/1/g;
				$text =~ s/\bdv[ae]\b/2/g;
				$text =~ s/\btri\b/3/g;
				$text =~ s/\bštiri\b/4/g;
				$text =~ s/\bpet\b/5/g;
				$text =~ s/\bšest\b/6/g;

				my @all_matches = $text =~ m/(\d+ [\wčšžćđČŠŽĆĐ]+)/g if $text;
				my $road = my $dead = my $calls = my $breaks = my $steals = my $robberies = my $violence = my $damage = my $threat = my $peace = my $felonies = my $interventions = 0;

				foreach my $what (reverse @all_matches) { # reverse to fix duplicates and repeats
					$road = $1 if ($what =~ m/(\d+) prometn/g);
					$dead = $1 if ($what =~ m/(\d+) umrl/g);
					$calls = $1 if ($what =~ m/(\d\.?\d+?) klic/g);
						$calls =~ s/\.//g;
					$breaks = $1 if ($what =~ m/(\d+) vlom/g);
					$steals = $1 if ($what =~ m/(\d+) tatv/g);
					$robberies = $1 if ($what =~ m/(\d+) rop/g);
					$violence = $1 if ($what =~ m/(\d+) nasilj/g);
					$damage = $1 if ($what =~ m/(\d+) poškodo/g);
					$threat = $1 if ($what =~ m/(\d+) grož/g);
					$peace = $1 if ($what =~ m/(\d+) krš/g);
					$peace = $1 if ($what =~ m/Javni red in mir je bil kršen (\d+)/);
					$peace = $1 if ($what =~ m/(\d+) intervencij zaradi kršitev javnega/);
					$felonies = $1 if ($what =~ m/(\d+) kazn/g);
					$interventions = $1 if ($what =~ m/(\d+) interv/g);
				} 			
# output
				$text =~ s/\r?\n/ /gs if $text;
				$text =~ s/^\s+//gs if $text;
				$text =~ s/\((\d+)\)/$1/gs if $text;
				
				print join("\t", $d, $month, $y, $url, $title, $calls, $interventions, $road, $peace, $felonies, $breaks, $damage, $steals, $robberies, $violence, $threat, $dead, $text)."\n" if ($title =~ /pregled/i and $title !~ /promet/i);	
				
				$stats{'road'} += $road;
				$stats{'dead'} += $dead;
				$stats{'calls'} += $calls;
				$stats{'interventions'} += $interventions;
				$stats{'peace'} += $peace;
				$stats{'felonies'} += $felonies;
				$stats{'breaks'} += $breaks;
				$stats{'damage'} += $damage;
				$stats{'steals'} += $steals;
				$stats{'robberies'} += $robberies;
				$stats{'violence'} += $violence;
				$stats{'threat'} += $threat;

# debug
#				if ($d == 21 and $m eq 'apr' and $y == 2020) {
#					warn Dumper $text;
#					warn Dumper @all_matches;
#					warn Dumper $1 if ($text =~ m/(\d+) interv/g);
#					warn Dumper $1 if ($text =~ m/(\d+) krš/g);

#					warn join("\t", $d, $m, $y, $url, $title, $calls, $interventions, $road, $peace, $felonies, $breaks, $damage, $steals, $robberies, $violence, $threat, $dead, $text)."\n";
#				}
			}
		}
	}
}

my $total = 0;
foreach my $what (keys(%stats)) {
	warn $what."\t".$stats{$what};
	$total += $stats{$what};
}
warn "total: ".$total;

#<div class='article'><div class='datebox'><span class='day'>29.</span><span class='month'>feb.</span><span class='year'>2008</span></div><div class='datetext'><a href='/medijsko-sredisce/dogodki-v-zadnjih-24-urah/41857--sp-19923'><h4>V Ljubljani je bil ukraden Renault clio</h4></a></div></div>
#
#<div class='article'><div class='datebox'><span class='day'>5.</span><span class='month'>apr.</span><span class='year'>2015</span></div><div class='datetext'><a href='/medijsko-sredisce/dogodki-v-zadnjih-24-urah/77521-kratek-statistini-pregled-dogajanj-v-zadnjih-24-urah-sp-2481'><h4>Kratek statistični pregled dogajanj v zadnjih 24 urah</h4></a><p>V zadnjih 24 urah je bilo na interventni številki policije »113« sprejetih 1157 klicev. Med 440 interventnimi dogodki, smo policisti med drugim obravnavali 73 prometnih nesreč, 75 kršitev javnega reda in miru ter 78 kaznivih dejanj.
#Med kaznivimi dejanji smo zabeležili 42 tatvin, 16 vlomov, 13 poškodovanj tuje stvari, 2 kaznivi dejanji nasilja v družini ter po 1 kaznivo dejanje povzročitve telesne poškodbe, ponarejanje listin, drzna tatvina, grožnja in kaznivo dejanje v zvezi s prepovedanimi drogami.
#Da bi zaščitili žrtve nasilja v družini, smo 2 osebama izrekli ukrep prepovedi približevanja.
#Zaradi kršitev javnega reda in miru smo opravili 48 intervencij na javnem kraju, 27 intervencij pa v zasebnih prostorih. 4 kršitelji so bili pridržani.
#Zaradi storitve hujših prekrškov v cestnem prometu smo 8 voznikom zasegli vozila in pridržali 1 voznika.
#V 63 prometnih nesrečah je nastala premoženjska škoda, v 10 nesrečah pa so bili udeleženci lažje telesno poškodovani.</p><p align='right'><a href='/medijsko-sredisce/dogodki-v-zadnjih-24-urah/77521-kratek-statistini-pregled-dogajanj-v-zadnjih-24-urah-sp-2481'>Več</a></p></div></div>


# 30	apr	2011	/medijsko-sredisce/dogodki-v-zadnjih-24-urah/58865-kratek-statistini-pregled-dogajanj-v-noi-na-3042011	Kratek statistični pregled dogajanj v noči na 30. 4. 2011	V minuli noči so policisti po vsej Sloveniji obravnavali 34 prometnih nesreč, 84 kr&scaron;itev javnega reda in miru in 41 kaznivih dejanj. &nbsp; V 29 prometnih nesrečah je nastala premoženjska &scaron;koda, v preostalih 5 nesrečah pa so 3 osebe umrle, 9 pa jih je bilo lahko telesno po&scaron;kodovanih. Zaradi vožnje pod vplivom alkohola je bilo&nbsp; do streznitve pridržanih 18 voznikov, od tega po 5 v Ljubljani in Mariboru, 3 v Kopru, 2 v Novi Gorici, ter po 1 v Kranju, Novem mestu in Celju. &nbsp; Zaradi kr&scaron;itev javnega reda in miru so policisti opravili 58 posegov na javnem kraju, 26 pa v zasebnih prostorih. Do streznitve je bil pridržan 1 kr&scaron;itelj v Ljubljani. &nbsp; Med obravnavanimi kaznivimi dejanji je bilo 17 tatvin, 10 po&scaron;kodovanj tuje stvari, 7 vlomov, 2 ponarejanji listin, ter po 1 rop, huda telesna po&scaron;kodba, nasilje v družini, surovo ravnanje in kr&scaron;itev nedotakljivosti stanovanja.
# 2	apr	2020	/medijsko-sredisce/dogodki-v-zadnjih-24-urah/103473-kratek-statisticni-pregled-dogajanj-v-zadnjih-24-urah-311	Kratek statistični pregled dogajanj v zadnjih 24 urah	V preteklih 24 urah smo na interventno številko policije "113" sprejeli 1603 klice. Med 447 interventnimi klici, na podlagi katerih smo policisti posredovali, je bilo 12 dogodkov takih, ki so terjali nujno ukrepanje. Med drugim smo obravnavali tudi 43 prometnih nesreč, 100 kršitev javnega reda in miru, ter 53 kaznivih dejanj. Na področju prometne varnosti smo obravnavali 41 prometnih nesreč s premoženjsko škodo, 1 nesrečo z lahkimi telesnimi poškodbami in 1 s hudimi. Zaradi hujših kršitev cestnoprometnih predpisov smo zasegli 5 vozil in sicer 2 na območju Policijske uprave Novo mesto, ter po 1 vozilo na območju policijskih uprav Ljubljana, Maribor in Celje. Javni red in mir je bil kršen v 77 primerih na javnih krajih, ter 23-krat v zasebnih prostorih. Pridržali smo 5 kršiteljev in sicer po 2 na območju policijskih uprav Ljubljana in Celje in 1 na območju Policijske uprave Kranj. Zaradi zaščite žrtev nasilja v družini smo 4 osebam na območju policijskih uprav Maribor, Celje in Nova Gorica izrekli ukrep prepovedi približevanja. Med kaznivimi dejanji je bilo 19 vlomov, 17 tatvin, 2 drzni tatvini, 1 rop, 6 poškodovanj tuje stvari, 3 nasilja v družini, 3 povzročitve telesnih poškodb, 1 kaznivo dejanje v zvezi s prepovednimi drogami in 1 grožnja.

# <div class='article'><div class='datebox'><span class='day'>5.</span><span class='month'>apr.</span><span class='year'>2011</span></div><div class='datetext'><a href='/medijsko-sredisce/dogodki-v-zadnjih-24-urah/34419--sp-25664'><h4>Kratek statistični pregled dogajanj v noči na 5.4.2011.</h4></a></div></div>
