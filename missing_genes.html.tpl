<!DOCTYPE html>
<html lang="en">
	<head>
		<title>Genes not found in Human Brain Transcriptome</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" type="text/css" href="http://hbatlas.org/css/cake.generic.css" />
		<link rel="stylesheet" type="text/css" href="http://hbatlas.org/css/hba.css" />
	</head>
	<body>
		<div id="head"></div>
		<h1>Genes not found in Human Brain Transcriptome</h1>
		<ul>
			{% for gene in genes %}
			<li><a href="http://hbatlas.org/hbtd/basicSearch.pl?geneNameType=Gene+official+symbol&geneName={{ gene | urlencode }}&region=Brain+regions">{{ gene }}</a></li>
			{% endfor %}
		</ul>
	</body>
</html>
