if [ -z ${1+x} ]; then
	version=$(cat core.py | grep "version = " | sed 's/version = //' | sed\
	's/\"$//' | sed 's/-.*//')
else
	vesrion=$(echo \"$1)
fi

commit=$(git log --oneline -n 1 | sed 's/ .*//')
echo $version-$commit\"
versionstr=$(echo $version-$commit\")

echo "Updating version to $versionstr. Is this correct? [y/n]"
say "Updating version to $versionstr. Is this correct?" &
read check
if [ $check != 'y' ]; then
	echo 'Exiting!'
	say 'Exiting!' &
	exit
fi

sed -i '' "s/version = \".*\"/version = $versionstr/" core.py
