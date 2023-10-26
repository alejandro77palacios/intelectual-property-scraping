for d in ./2005/*/ ; do
    dir_name=$(basename "$d")
    aws s3 cp "$d" "s3://test-pjds-data/data/2005/$dir_name/" --recursive --exclude "*.DS_Store"
done
