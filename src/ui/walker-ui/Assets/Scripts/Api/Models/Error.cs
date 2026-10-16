using System;

namespace Api.Models {
    [Serializable]
    public class Error : ApiModel<Error> {
        public int status;
        public string message;
        public string code;
    }
}
