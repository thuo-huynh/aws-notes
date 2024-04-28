const sharp = require("sharp")
const aws = require("aws-sdk")
const s3 = new aws.S3()

const width = parseInt(process.env.WIDTH);
const height = parseInt(process.env.HEIGHT);
const destinationBucket = process.env.DES_BUCKET;

exports.handler = async function(event, context){
    if (event.Records[0].eventName === "ObjectRemove:Delete"){
        return;
    }
    const BUCKET = event.Records[0].s3.bucket.name;
    const KEY = event.Records[0].s3.object.key;
    try {
        let image = await s3.getObject({ Bucket: BUCKET, Key: KEY }).promise();
        image = await sharp(image.Body)
        const resizeImage = await image.resize(width, height, {fit: sharp.fit.fill, withoutEnlargement: true}).toBuffer();
        await s3.putObject({ Bucket: destinationBucket, Body: resizeImage, Key: KEY }).promise();
        await s3.deleteObject({ Bucket: BUCKET, Key: KEY }).promise();
        return;
    } catch (err) {
        context.fail(`Error resizing image: ${err} `);
    }
}