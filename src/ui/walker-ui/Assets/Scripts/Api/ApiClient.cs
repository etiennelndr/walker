using System;

using Api.Models;

using UnityEngine;
using UnityEngine.Networking;

namespace Api {
    public class ApiClient {
        private readonly string _baseUrl;

        public ApiClient(string baseUrl) {
            _baseUrl = baseUrl.TrimEnd('/');
        }

        public async Awaitable CreateRecord(Record record) {
            await Post("/records", record.Encode());
        }

        // Sends a JSON body to the API and returns the body of the response. Throws an ApiException
        // if the server is unreachable or answers with an error status.
        private async Awaitable<string> Post(string path, string json) {
            string url = _baseUrl + path;
            using UnityWebRequest request = UnityWebRequest.Post(url, json, "application/json");
            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success) {
                return request.downloadHandler.text;
            }

            Error error = ReadError(request);
            string message = error != null
                ? $"POST {url} failed: {error.code} {error.message}"
                : $"POST {url} failed: {request.responseCode} {request.error}";

            throw new ApiException(message, request.responseCode, error);
        }

        // Returns the error sent by the API for a failed request, or null if there is none: only
        // validation and internal errors have one, other failures (unknown route, unreachable
        // server, etc.) have no body or an HTML one.
        private static Error ReadError(UnityWebRequest request) {
            string contentType = request.GetResponseHeader("Content-Type") ?? "";
            return contentType.StartsWith("application/json", StringComparison.OrdinalIgnoreCase)
                ? Error.Decode(request.downloadHandler.text)
                : null;
        }
    }
}
