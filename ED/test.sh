for i in $(seq 1 1 1)
do
    echo "dealing with ${i}:";
    python ./validation.py \
    --load_name "./models/v4_SPA/v4_SPA.pth" \
    --save_name "../images/output/ED" \
    --baseroot "../images" ;
done