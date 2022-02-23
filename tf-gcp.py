CONNECT TYPEFORM

return await require("@pipedream/platform").axios(this, {
  url: `https://api.typeform.com/me`,
  headers: {
    Authorization: `Bearer ${auths.typeform.oauth_access_token}`,
  },
})










CONNECT GOOGLE CLOUD

// Required workaround to get the @google-cloud/storage package
// working correctly on Pipedream
require("@dylburger/umask")()

const { Storage } = require('@google-cloud/storage')

const key = JSON.parse(auths.google_cloud.key_json)
 
// Creates a client from a Google service account key.
// See https://cloud.google.com/nodejs/docs/reference/storage/1.6.x/global#ClientConfig
const storage = new Storage({
  projectId: key.project_id,
  credentials: {
    client_email: key.client_email,
    private_key: key.private_key,
  }
})

// Uncomment this section and rename for your bucket before running this code
// const bucketName = 'pipedream-test-bucket';

await storage.createBucket(bucketName)
console.log(`Bucket ${bucketName} created.`)
