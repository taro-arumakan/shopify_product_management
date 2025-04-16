const SHOPNAME = "yyy"
const ACCESS_TOKEN = "xxx";

function testReq() {
  const query = `{
     products(first: 3) {
       edges {
         node {
           id
           title
         }
       }
   }}`;
  const ret = req(query);
  console.log(ret);
}

function getDriveImageDetails(folderId, sku, imagePrefix) {
  var folder = DriveApp.getFolderById(folderId);
  var files = [];
  var filesItr = folder.getFiles();
  while (filesItr.hasNext()) {
    var file = filesItr.next();
    files.push(file);
  }

  // Sort the files using natural order (considering numeric parts)
  files.sort(function (a, b) {
    return naturalCompare(a.getName(), b.getName());
  });

  var res = [];
  var sequence = 0;

  for (let file of files) {
    if (file.getMimeType().startsWith('image/')) {
      res.push({
        name: `${imagePrefix}_${sku}_${String(sequence).padStart(2, '0')}_${file.getName()}`,
        mimeType: file.getMimeType(),
        size: file.getSize(),
        downloadUrl: file.getDownloadUrl()
      });
      sequence++;
    }
  }
  return res;
}

// Function to compare two strings in a natural order (considering numeric parts)
function naturalCompare(a, b) {
  return a.toLowerCase().localeCompare(b.toLowerCase(), undefined, { numeric: true, sensitivity: 'base' });
}

function run_query(query, variables, method = 'post', resource = 'graphql') {
  const url = `https://${SHOPNAME}.myshopify.com/admin/api/2024-07/${resource}.json`
  const options = {
    'method': method,
    'payload': JSON.stringify({ query: query, variables: variables }),
    'muteHttpExceptions': true,
    'headers': {
      "X-Shopify-Access-Token": ACCESS_TOKEN,
      "Content-type": "application/json"
    }
  };
  Logger.log(options);
  return UrlFetchApp.fetch(url, options);
}

function generateStagedUploadTargets(files) {
  var query = `
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  var variables = {
    input: files.map(file => ({
      resource: "IMAGE",
      filename: `test_upload_${file.name}`,
      mimeType: file.mimeType,
      httpMethod: "POST",
      // fileSize: file.size
    }))
  };

  var response = run_query(query, variables);
  var json = JSON.parse(response.getContentText());
  Logger.log(json.data.stagedUploadsCreate.stagedTargets.map(node => node.resourceUrl));

  return json.data.stagedUploadsCreate.stagedTargets;
}

function uploadImagesToShopify(stagedTargets, files) {
  for (var i = 0; i < stagedTargets.length; i++) {
    var target = stagedTargets[i];
    var file = files[i];

    var payload = {
      'Content-Type': file.mimeType, // Equivalent to -F "Content-Type=image/png"
      'success_action_status': '201', // Equivalent to -F "success_action_status=201"
      'acl': 'private', // Equivalent to -F "acl=private"
      'file': UrlFetchApp.fetch(file.downloadUrl).getBlob().setName(file.name) // Equivalent to -F "file=@/path/to/file.png"
    };

    // Add all the parameters returned by stagedUploadsCreate to the payload
    target.parameters.forEach(function (param) {
      payload[param.name] = param.value;
    });

    var options = {
      'method': 'post',
      'payload': payload,
      'muteHttpExceptions': true // Ensure you get the response even in case of an error
    };

    Logger.log(`Uploading file: ${file.name} to ${target.url} which is accessed through ${target.resourceUrl}`);
    var response = UrlFetchApp.fetch(target.url, options);
    Logger.log(`upload response: ${response}`);
  }
}

function productIdByTitle(title) {
  query = `
    query productsByQuery($query_string: String!)
    {
      products(first: 10, query: $query_string, sortKey: TITLE) {
        nodes {
          id
          title
        }
      }
    }
  `;
  var variables = {
    query_string: `Title: '${title}'`
  };
  var response = run_query(query, variables);
  var json = JSON.parse(response.getContentText());
  if (json.data.products.nodes.length !== 1) {
    throw new Error(`multiple products found for ${title}: ${json.data.products.nodes}`);
  }
  return json.data.products.nodes[0].id;
}

function assignImagesToProduct(resourceUrls, alts, productId) {
  var mutationQuery = `
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        userErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
  `;

  var medias = [];
  for (var i = 0; resourceUrls.length; i++) {
    medias.push({
      originalSource: resourceUrls[i],
      alt: alts[i],
      mediaContentType: 'IMAGE'
    })
  }
  var variables = {
    media: medias,
    productId: productId
  };

  var response = run_query(mutationQuery, variables);
  var json = JSON.parse(response.getContentText());

  Logger.log("Initial media status:");
  Logger.log(JSON.stringify(json));

  if (json.data.productCreateMedia.userErrors.length > 0) {
    throw new Error("Error during media creation: " + JSON.stringify(json.data.productCreateMedia.userErrors));
  }

  var status = waitForMediaProcessingCompletion(productId);
  if (!status) {
    throw new Error("Error during media processing");
  }

}

function productMediaStatus(productId) {
  const query = `
    query ProductMediaStatusByID($productId: ID!) {
      product(id: $productId) {
        media(first: 30) {
          nodes {
            id
            alt
            mediaContentType
            status
            mediaErrors {
              code
              details
              message
            }
            mediaWarnings {
              code
              message
            }
          }
        }
      }
    }
  `;

  const variables = { productId: productId };
  const response = run_query(query, variables);
  const json = JSON.parse(response.getContentText());
  return json.data.product.media.nodes;
}

function waitForMediaProcessingCompletion(productId, timeoutMinutes = 10) {
  const pollInterval = 30000; // Poll every 30 seconds
  const maxAttempts = (timeoutMinutes * 60 * 1000) / pollInterval;
  let attempts = 0;

  while (attempts < maxAttempts) {
    const mediaNodes = productMediaStatus(productId);
    const processingItems = mediaNodes.filter(node => node.status === "PROCESSING");
    const failedItems = mediaNodes.filter(node => node.status === "FAILED");

    if (failedItems.length > 0) {
      Logger.log("Some media failed to process:");
      failedItems.forEach(item => {
        Logger.log(`Status: ${item.status}, Errors: ${JSON.stringify(item.mediaErrors)}`);
      });
      return false;
    }

    if (processingItems.length === 0) {
      Logger.log("All media have completed processing.");
      return true;
    }

    Logger.log("Media still processing. Waiting...");
    Utilities.sleep(pollInterval);
    attempts++;
  }

  Logger.log("Timeout reached while waiting for media processing completion.");
  return false;
}

function removeProductMediaByProductId(productId) {
  var mediaNodes = productMediaStatus(productId);
  var mediaIds = mediaNodes.map(node => node.id);
  if (!mediaIds) {
    Logger.log(`nothing to delete for ${productId}`);
    return true;
  } else {
    Logger.log(`going to delete ${mediaIds} from ${productId}`);

    var query = `
      mutation deleteProductMedia($productId: ID!, $mediaIds: [ID!]!) {
        productDeleteMedia(productId: $productId,  mediaIds: $mediaIds) {
          deletedMediaIds
          product {
            id
          }
          mediaUserErrors {
            code
            field
            message
          }
        }
      }
    `

    variables = {
      productId: productId,
      mediaIds: mediaIds
    };
    var response = run_query(query, variables);
    Logger.log(response);
    return response;
  }
}

function uploadAndAssignImagesToProduct(productId, driveImageDetails) {
  var stagedTargets = generateStagedUploadTargets(driveImageDetails);
  uploadImagesToShopify(stagedTargets, driveImageDetails);
  Logger.log(`images uploaded for ${productId}, going to remove existing and assign.`);
  removeProductMediaByProductId(productId);
  assignImagesToProduct(stagedTargets.map(target => target.resourceUrl), productId);
}

function varintIdForSku(sku) {
  var query = `
    {
      productVariants(first: 10, query: "sku:'${sku}'") {
        nodes {
          id
          title
        }
      }
    }
  `
  var response = run_query(query, {});
  var json = JSON.parse(response.getContentText());
  if (json.data.productVariants.nodes.length !== 1) {
    throw new Error(`multiple variants found for ${sku}: ${json.data.productVariants.nodes}`);
  }
  return json.data.productVariants.nodes[0].id;
}

function variantByVariantId(variantId) {
  var query = `
    {
      productVariant(id:"${variantId}") {
        id
        title
        media(first: 5) {
          nodes {
            id
          }
        }
      }
    }
  `
  var response = run_query(query, {});
  Logger.log(response);
  var json = JSON.parse(response.getContentText());
  return json.data.productVariant;
}

function dettachVariantMedia(productId, variantId, mediaId) {
  var query = `
    mutation productVariantDetachMedia($productId: ID!, $variantMedia: [ProductVariantDetachMediaInput!]!) {
      productVariantDetachMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
          media(first: 5) {
            nodes {
              id
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `
  var variables = {
    productId: productId,
    variantMedia: [{
      variantId: variantId,
      mediaIds: [mediaId]
    }]
  }
  return run_query(query, variables);
}

function assignImageToSKUs(productId, imagePosition, skus) {
  var variantIds = skus.map(sku => varintIdForSku(sku));

  var variants = variantIds.map(variantId => variantByVariantId(variantId));
  for (var variant of variants) {
    if (variant.media.nodes.length > 0) {
      dettachVariantMedia(productId, variant.id, variant.media.nodes[0].id);
    }
  };

  var mediaNodes = productMediaStatus(productId);
  var mediaId = mediaNodes[imagePosition].id;

  var query = `
    mutation productVariantAppendMedia($productId: ID!, $variantMedia: [ProductVariantAppendMediaInput!]!) {
      productVariantAppendMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
  `
  var variables = {
    productId: productId,
    variantMedia: variantIds.map(vid => ({
      variantId: vid,
      mediaIds: [mediaId]
    }))
  };

  return run_query(query, variables)

}
function processProductImagesToShopify(imagePrefix, productTitle, driveIds, skuss) {
  /**
   * Processes and uploads images for a product to Shopify, associating them with
   * specific SKUs based on their positions within provided Google Drive folders.
   *
   * @param {string} imagePrefix - A prefix to be added to each image file name during processing.
   * @param {string} productTitle - The title of the product in Shopify. Used to retrieve the product ID.
   * @param {string[]} driveIds - An array of Google Drive folder IDs, each containing images for different color variants of the product.
   * @param {string[][]} skuss - A nested array of SKUs. Each inner array corresponds to a Google Drive folder and contains SKUs for different sizes of the same color variant.
   *
   * Example:
   *  productTitle = 'Twisted Neck Superfine Merino Wool Cardigan'
   *  driveIds = [
   *    '1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ',
   *    '1ACt4g7tqigsmXYemUCc9KnDynW20E5Iz',
   *    '15VwlvmnC7EBmOZaslyMq40KyHXcWt63g'
   *  ]
   *  skuss = [
   *    ['KM-24FW-SW01-IV-S', 'KM-24FW-SW01-IV-M'],
   *    ['KM-24FW-SW01-MT-S', 'KM-24FW-SW01-MT-M'],
   *    ['KM-24FW-SW01-DBR-S', 'KM-24FW-SW01-DBR-M']
   *  ]
   *
   * This will:
   *  1. Add all images from the three folders to the product 'Twisted Neck Superfine Merino Wool Cardigan'.
   *  2. Assign the first image from each folder as the variant image for the corresponding SKUs.
   *     For instance, the first image in '1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ' will be assigned
   *     to the SKUs 'KM-24FW-SW01-IV-S' and 'KM-24FW-SW01-IV-M'.
   */

  var productId = productIdByTitle(productTitle);
  Logger.log(`processing ${imagePrefix} - ${productTitle}, ${productId}, ${skuss}, ${driveIds}`);
  var driveImageDetails = [];
  var variantImagePositions = [];
  for (var i = 0; i < driveIds.length; i++) {
    variantImagePositions.push(driveImageDetails.length);
    driveImageDetails = driveImageDetails.concat(getDriveImageDetails(driveIds[i], skuss[i][0], imagePrefix));
  }
  Logger.log(driveImageDetails);
  uploadAndAssignImagesToProduct(productId, driveImageDetails);
  for (var i = 0; i < variantImagePositions.length; i++) {
    assignImageToSKUs(productId, variantImagePositions[i], skuss[i]);
  }
}

function test() {
  var imagePrefix = new Date().toLocaleTimeString("ja-JP", { year: "numeric", month: "2-digit", day: "2-digit" }).replaceAll(/[^0-9]/g, '')
  var productTitle = 'Twisted Neck Superfine Merino Wool Cardigan';
  var driveIds = ['1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ',
    '1ACt4g7tqigsmXYemUCc9KnDynW20E5Iz',
    '15VwlvmnC7EBmOZaslyMq40KyHXcWt63g'];
  var skuss = [
    ['KM-24FW-SW01-IV-S',
      'KM-24FW-SW01-IV-M'],
    ['KM-24FW-SW01-MT-S',
      'KM-24FW-SW01-MT-M'],
    ['KM-24FW-SW01-DBR-S',
      'KM-24FW-SW01-DBR-M']
  ];
  processProductImagesToShopify(imagePrefix, productTitle, driveIds, skuss);
  // var productId = productIdByTitle('Hidden Button Pintucked Jacket');
  // var variantImagePositions = [0, 8];
  // var skuss = [
  //   ['KM-24FW-JK01-DBE-F'],
  //   ['KM-24FW-JK01-BK-F']
  // ];
  // for (var i = 0; i < variantImagePositions.length; i++) {
  //   var response = assignImageToSKUs(productId, variantImagePositions[i], skuss[i]);
  //   Logger.log(response);
  // }

}
