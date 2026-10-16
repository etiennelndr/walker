using System;

using Api.Models;

namespace Api {
    public class ApiException : Exception {
        public ApiException(string message, long responseCode, Error error) : base(message) {
            ResponseCode = responseCode;
            Error = error;
        }

        public long ResponseCode { get; }
        public Error Error { get; }
    }
}
