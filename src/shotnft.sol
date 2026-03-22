// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title ShotNFT — Minimal ERC-721 for minting ShotSpec NFTs
contract ShotNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    
    event ShotMinted(uint256 indexed tokenId, address indexed to, string tokenURI);
    
    constructor() ERC721("0xAUTEUR Shot", "AUTEUR") Ownable(msg.sender) {}
    
    function mint(address to, string memory tokenURI_) public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);
        emit ShotMinted(tokenId, to, tokenURI_);
        return tokenId;
    }
    
    function totalSupply() public view returns (uint256) {
        return _nextTokenId;
    }
    
    // Required overrides
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
